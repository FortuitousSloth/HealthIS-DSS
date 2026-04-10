"""
load_data.py
Reads MI.data and loads it into the dss_db PostgreSQL database.
Raw '?' values are stored as NULL (no imputation — that stays in the model pipeline).

Run from the project root:
    python3 database/load_data.py
"""

import csv
import psycopg2

DATA_PATH = "data/MI.data"

DB_CONFIG = {
    "dbname": "dss_db",
    "user": None,       # defaults to your OS username
    "host": "localhost",
    "port": 5432,
}

# Raw column indices -> named fields (matches prep_data.py column_map)
COL = {
    "patient_id":  0,
    "age":         1,
    "sex":         2,
    # cv_history
    "inf_anam":    3,
    "stenok_an":   4,
    "fk_stenok":   5,
    "ibs_post":    6,
    "ibs_nasl":    7,
    "gb":          8,
    "sim_gipert":  9,
    "dlit_ag":    10,
    "zsn_a":      11,
    # arrhythmia_history
    "nr11":       12,
    "nr01":       13,
    "nr02":       14,
    "nr03":       15,
    "nr04":       16,
    "nr07":       17,
    "nr08":       18,
    # conduction_history
    "np01":       19,
    "np04":       20,
    "np05":       21,
    "np07":       22,
    "np08":       23,
    "np09":       24,
    "np10":       25,
    # endocrine_history
    "endocr_01":  26,
    "endocr_02":  27,
    "endocr_03":  28,
    # lung_history
    "zab_leg_01": 29,
    "zab_leg_02": 30,
    "zab_leg_03": 31,
    "zab_leg_04": 32,
    "zab_leg_06": 33,
    # admission_vitals
    "s_ad_kbrig": 34,
    "d_ad_kbrig": 35,
    # outcomes
    "fibr_preds": 112,
    "preds_tah":  113,
    "jelud_tah":  114,
    "fibr_jelud": 115,
    "a_v_blok":   116,
    "otek_lanc":  117,
    "razriv":     118,
    "dressler":   119,
    "zsn":        120,
    "rec_im":     121,
    "p_im_sten":  122,
    "let_is":     123,
}


def clean(value):
    """Convert '?' or empty string to None; otherwise return stripped string."""
    v = value.strip()
    return None if v in ("?", "") else v


def load_rows(path):
    rows = []
    with open(path, newline="") as f:
        reader = csv.reader(f)
        for line in reader:
            if not line:
                continue
            rows.append(line)
    return rows


def get(row, field):
    idx = COL[field]
    if idx >= len(row):
        return None
    return clean(row[idx])


def insert_all(conn, rows):
    cur = conn.cursor()
    counts = {t: 0 for t in [
        "patients", "cv_history", "arrhythmia_history", "conduction_history",
        "endocrine_history", "lung_history", "admission_vitals", "outcomes"
    ]}

    for row in rows:
        pid = get(row, "patient_id")
        if pid is None:
            continue  # skip rows with no ID

        # --- patients ---
        cur.execute(
            "INSERT INTO patients (patient_id, age, sex) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
            (pid, get(row, "age"), get(row, "sex"))
        )
        counts["patients"] += cur.rowcount

        # --- cv_history ---
        cur.execute("""
            INSERT INTO cv_history
                (patient_id, inf_anam, stenok_an, fk_stenok, ibs_post, ibs_nasl, gb, sim_gipert, dlit_ag, zsn_a)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING
        """, (
            pid,
            get(row, "inf_anam"), get(row, "stenok_an"), get(row, "fk_stenok"),
            get(row, "ibs_post"), get(row, "ibs_nasl"), get(row, "gb"),
            get(row, "sim_gipert"), get(row, "dlit_ag"), get(row, "zsn_a"),
        ))
        counts["cv_history"] += cur.rowcount

        # --- arrhythmia_history ---
        cur.execute("""
            INSERT INTO arrhythmia_history
                (patient_id, nr11, nr01, nr02, nr03, nr04, nr07, nr08)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING
        """, (
            pid,
            get(row, "nr11"), get(row, "nr01"), get(row, "nr02"), get(row, "nr03"),
            get(row, "nr04"), get(row, "nr07"), get(row, "nr08"),
        ))
        counts["arrhythmia_history"] += cur.rowcount

        # --- conduction_history ---
        cur.execute("""
            INSERT INTO conduction_history
                (patient_id, np01, np04, np05, np07, np08, np09, np10)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING
        """, (
            pid,
            get(row, "np01"), get(row, "np04"), get(row, "np05"), get(row, "np07"),
            get(row, "np08"), get(row, "np09"), get(row, "np10"),
        ))
        counts["conduction_history"] += cur.rowcount

        # --- endocrine_history ---
        cur.execute("""
            INSERT INTO endocrine_history
                (patient_id, endocr_01, endocr_02, endocr_03)
            VALUES (%s,%s,%s,%s) ON CONFLICT DO NOTHING
        """, (pid, get(row, "endocr_01"), get(row, "endocr_02"), get(row, "endocr_03")))
        counts["endocrine_history"] += cur.rowcount

        # --- lung_history ---
        cur.execute("""
            INSERT INTO lung_history
                (patient_id, zab_leg_01, zab_leg_02, zab_leg_03, zab_leg_04, zab_leg_06)
            VALUES (%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING
        """, (
            pid,
            get(row, "zab_leg_01"), get(row, "zab_leg_02"), get(row, "zab_leg_03"),
            get(row, "zab_leg_04"), get(row, "zab_leg_06"),
        ))
        counts["lung_history"] += cur.rowcount

        # --- admission_vitals ---
        cur.execute("""
            INSERT INTO admission_vitals (patient_id, s_ad_kbrig, d_ad_kbrig)
            VALUES (%s,%s,%s) ON CONFLICT DO NOTHING
        """, (pid, get(row, "s_ad_kbrig"), get(row, "d_ad_kbrig")))
        counts["admission_vitals"] += cur.rowcount

        # --- outcomes ---
        cur.execute("""
            INSERT INTO outcomes
                (patient_id, fibr_preds, preds_tah, jelud_tah, fibr_jelud,
                 a_v_blok, otek_lanc, razriv, dressler, zsn, rec_im, p_im_sten, let_is)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING
        """, (
            pid,
            get(row, "fibr_preds"), get(row, "preds_tah"), get(row, "jelud_tah"),
            get(row, "fibr_jelud"), get(row, "a_v_blok"), get(row, "otek_lanc"),
            get(row, "razriv"), get(row, "dressler"), get(row, "zsn"),
            get(row, "rec_im"), get(row, "p_im_sten"), get(row, "let_is"),
        ))
        counts["outcomes"] += cur.rowcount

    conn.commit()
    cur.close()
    return counts


def main():
    print(f"Reading {DATA_PATH} ...")
    rows = load_rows(DATA_PATH)
    print(f"  {len(rows)} rows found")

    print("Connecting to dss_db ...")
    conn = psycopg2.connect(**{k: v for k, v in DB_CONFIG.items() if v is not None})

    print("Inserting data ...")
    counts = insert_all(conn, rows)
    conn.close()

    print("\nRows inserted per table:")
    for table, n in counts.items():
        print(f"  {table:<25} {n}")
    print("\nDone.")


if __name__ == "__main__":
    main()

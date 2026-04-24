"""
db.py
Database connection and patient query utilities for the DSS app.
Reads DATABASE_URL from .env (never committed to git).
"""

import os
from typing import Optional
import psycopg2
import psycopg2.extras
import pandas as pd

# Load .env if present
_env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
if os.path.exists(_env_path):
    with open(_env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

DATABASE_URL = os.environ.get("DATABASE_URL")


def get_connection():
    return psycopg2.connect(DATABASE_URL)


# Columns the model expects, in exact order from prep_data.py
MODEL_COLUMNS = [
    "AGE", "SEX",
    "INF_ANAM", "STENOK_AN", "FK_STENOK", "IBS_POST", "IBS_NASL",
    "GB", "SIM_GIPERT", "DLIT_AG", "ZSN_A",
    "nr11", "nr01", "nr02", "nr03", "nr04", "nr07", "nr08",
    "np01", "np04", "np05", "np07", "np08", "np09", "np10",
    "endocr_01", "endocr_02", "endocr_03",
    "zab_leg_01", "zab_leg_02", "zab_leg_03", "zab_leg_04", "zab_leg_06",
    "S_AD_KBRIG", "D_AD_KBRIG",
]

_PATIENT_QUERY = """
SELECT
    p.patient_id,
    p.age        AS "AGE",
    p.sex        AS "SEX",
    cv.inf_anam  AS "INF_ANAM",
    cv.stenok_an AS "STENOK_AN",
    cv.fk_stenok AS "FK_STENOK",
    cv.ibs_post  AS "IBS_POST",
    cv.ibs_nasl  AS "IBS_NASL",
    cv.gb        AS "GB",
    cv.sim_gipert AS "SIM_GIPERT",
    cv.dlit_ag   AS "DLIT_AG",
    cv.zsn_a     AS "ZSN_A",
    a.nr11, a.nr01, a.nr02, a.nr03, a.nr04, a.nr07, a.nr08,
    c.np01, c.np04, c.np05, c.np07, c.np08, c.np09, c.np10,
    e.endocr_01, e.endocr_02, e.endocr_03,
    l.zab_leg_01, l.zab_leg_02, l.zab_leg_03, l.zab_leg_04, l.zab_leg_06,
    v.s_ad_kbrig AS "S_AD_KBRIG",
    v.d_ad_kbrig AS "D_AD_KBRIG",
    o.fibr_preds
FROM patients p
JOIN cv_history       cv USING (patient_id)
JOIN arrhythmia_history a USING (patient_id)
JOIN conduction_history c USING (patient_id)
JOIN endocrine_history  e USING (patient_id)
JOIN lung_history       l USING (patient_id)
JOIN admission_vitals   v USING (patient_id)
JOIN outcomes           o USING (patient_id)
WHERE p.patient_id = %s
"""


def fetch_patient(patient_id: int) -> Optional[dict]:
    """Return a dict with all fields for a given patient_id, or None if not found."""
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(_PATIENT_QUERY, (patient_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return dict(row) if row else None


def fetch_all_patient_ids() -> list:
    """Return sorted list of all patient_ids in the database."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT patient_id FROM patients ORDER BY patient_id")
        ids = [r[0] for r in cur.fetchall()]
        cur.close()
        conn.close()
        return ids
    except Exception:
        return []


def patient_to_features(row: dict, fill_values: dict) -> pd.DataFrame:
    """
    Convert a patient row (from fetch_patient) into a single-row DataFrame
    with columns in MODEL_COLUMNS order.
    NULLs are filled using fill_values (medians/modes from training data).
    """
    data = {}
    for col in MODEL_COLUMNS:
        val = row.get(col)
        if val is None:
            val = fill_values.get(col)
        data[col] = [val]
    return pd.DataFrame(data, columns=MODEL_COLUMNS)

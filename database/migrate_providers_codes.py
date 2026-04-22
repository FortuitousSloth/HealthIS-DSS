"""
migrate_providers_codes.py
--------------------------
1. Creates the `providers` table (20 synthetic ER physicians)
2. Adds provider_id FK column to `patients` and randomly assigns providers
3. Creates `clinical_codes` reference table mapping every model variable
   to its LOINC or ICD-10 code + description
Run once:
    /Library/Developer/CommandLineTools/usr/bin/python3 database/migrate_providers_codes.py
"""

import os, random, sys
import psycopg2

# ── Load .env ────────────────────────────────────────────────────────────────
_env = os.path.join(os.path.dirname(__file__), "..", ".env")
if os.path.exists(_env):
    with open(_env) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

DATABASE_URL = os.environ["DATABASE_URL"]
conn = psycopg2.connect(DATABASE_URL)
conn.autocommit = False
cur = conn.cursor()

# ── 1. PROVIDERS TABLE ────────────────────────────────────────────────────────
print("Creating providers table...")
cur.execute("DROP TABLE IF EXISTS providers CASCADE;")
cur.execute("""
CREATE TABLE providers (
    provider_id   SERIAL PRIMARY KEY,
    full_name     TEXT NOT NULL,
    specialty     TEXT NOT NULL DEFAULT 'Emergency Medicine'
);
""")

PROVIDERS = [
    "Dr. James Okafor",
    "Dr. Maria Chen",
    "Dr. Robert Patel",
    "Dr. Sarah Nguyen",
    "Dr. David Kim",
    "Dr. Emily Torres",
    "Dr. Michael Hassan",
    "Dr. Priya Sharma",
    "Dr. Andrew Kowalski",
    "Dr. Lauren Brooks",
    "Dr. Kevin Mbeki",
    "Dr. Rachel Goldstein",
    "Dr. Thomas Rivera",
    "Dr. Aisha Williams",
    "Dr. Jonathan Lee",
    "Dr. Fatima Al-Rashid",
    "Dr. Brian Fitzgerald",
    "Dr. Nina Petrov",
    "Dr. Carlos Reyes",
    "Dr. Megan O'Sullivan",
]

cur.executemany(
    "INSERT INTO providers (full_name, specialty) VALUES (%s, 'Emergency Medicine')",
    [(name,) for name in PROVIDERS]
)
print(f"  Inserted {len(PROVIDERS)} providers.")

# ── 2. ADD provider_id TO patients ───────────────────────────────────────────
print("Adding provider_id column to patients...")
cur.execute("""
ALTER TABLE patients
    ADD COLUMN IF NOT EXISTS provider_id INTEGER REFERENCES providers(provider_id);
""")

# Fetch all patient ids
cur.execute("SELECT patient_id FROM patients ORDER BY patient_id;")
patient_ids = [r[0] for r in cur.fetchall()]

# Randomly assign one of 20 providers to each patient (reproducible seed)
random.seed(42)
assignments = [(random.randint(1, len(PROVIDERS)), pid) for pid in patient_ids]
cur.executemany(
    "UPDATE patients SET provider_id = %s WHERE patient_id = %s",
    assignments
)
print(f"  Assigned providers to {len(patient_ids)} patients.")

# ── 3. CLINICAL CODES REFERENCE TABLE ────────────────────────────────────────
print("Creating clinical_codes reference table...")
cur.execute("DROP TABLE IF EXISTS clinical_codes CASCADE;")
cur.execute("""
CREATE TABLE clinical_codes (
    code_id         SERIAL PRIMARY KEY,
    variable_name   TEXT NOT NULL,
    table_name      TEXT NOT NULL,
    code_system     TEXT NOT NULL,   -- 'LOINC' or 'ICD-10-CM'
    code_value      TEXT NOT NULL,
    code_description TEXT NOT NULL
);
""")

CODES = [
    # ── Demographics / Vitals (LOINC) ─────────────────────────────────────
    ("age",          "patients",         "LOINC",     "30525-0",  "Age"),
    ("sex",          "patients",         "LOINC",     "76689-9",  "Sex assigned at birth"),
    ("s_ad_kbrig",   "admission_vitals", "LOINC",     "8480-6",   "Systolic blood pressure"),
    ("d_ad_kbrig",   "admission_vitals", "LOINC",     "8462-4",   "Diastolic blood pressure"),

    # ── Cardiovascular history (ICD-10-CM) ────────────────────────────────
    ("inf_anam",     "cv_history",       "ICD-10-CM", "I25.2",    "Old myocardial infarction (prior MI count)"),
    ("stenok_an",    "cv_history",       "ICD-10-CM", "I20.9",    "Angina pectoris, unspecified (severity)"),
    ("fk_stenok",    "cv_history",       "ICD-10-CM", "I20.8",    "Other forms of angina pectoris (functional class)"),
    ("ibs_post",     "cv_history",       "ICD-10-CM", "I25.10",   "Atherosclerotic heart disease, unspecified (post-MI IHD)"),
    ("ibs_nasl",     "cv_history",       "ICD-10-CM", "Z82.49",   "Family history of ischemic heart disease"),
    ("gb",           "cv_history",       "ICD-10-CM", "I10",      "Essential (primary) hypertension"),
    ("sim_gipert",   "cv_history",       "ICD-10-CM", "I15.9",    "Secondary hypertension, unspecified (symptomatic)"),
    ("dlit_ag",      "cv_history",       "ICD-10-CM", "I10",      "Duration of hypertension (mapped to I10)"),
    ("zsn_a",        "cv_history",       "ICD-10-CM", "I50.9",    "Heart failure, unspecified (history)"),

    # ── Arrhythmia history (ICD-10-CM) ───────────────────────────────────
    ("nr11",         "arrhythmia_history", "ICD-10-CM", "I49.9",  "Cardiac arrhythmia, unspecified (history flag)"),
    ("nr01",         "arrhythmia_history", "ICD-10-CM", "I49.1",  "Atrial premature depolarization"),
    ("nr02",         "arrhythmia_history", "ICD-10-CM", "I47.1",  "Supraventricular tachycardia"),
    ("nr03",         "arrhythmia_history", "ICD-10-CM", "I48.0",  "Paroxysmal atrial fibrillation"),
    ("nr04",         "arrhythmia_history", "ICD-10-CM", "I48.11", "Longstanding persistent atrial fibrillation"),
    ("nr07",         "arrhythmia_history", "ICD-10-CM", "I49.3",  "Ventricular premature depolarization"),
    ("nr08",         "arrhythmia_history", "ICD-10-CM", "I47.2",  "Ventricular tachycardia"),

    # ── Conduction history (ICD-10-CM) ───────────────────────────────────
    ("np01",         "conduction_history", "ICD-10-CM", "I45.5",  "Other specified heart block (sinoatrial block)"),
    ("np04",         "conduction_history", "ICD-10-CM", "I44.0",  "Atrioventricular block, first degree"),
    ("np05",         "conduction_history", "ICD-10-CM", "I45.10", "Right bundle-branch block, unspecified"),
    ("np07",         "conduction_history", "ICD-10-CM", "I45.10", "Incomplete right bundle-branch block"),
    ("np08",         "conduction_history", "ICD-10-CM", "I45.10", "Complete right bundle-branch block"),
    ("np09",         "conduction_history", "ICD-10-CM", "I44.60", "Fascicular block, unspecified (incomplete LBBB)"),
    ("np10",         "conduction_history", "ICD-10-CM", "I44.7",  "Left bundle-branch block, unspecified"),

    # ── Endocrine history (ICD-10-CM) ─────────────────────────────────────
    ("endocr_01",    "endocrine_history",  "ICD-10-CM", "E11.9",  "Type 2 diabetes mellitus without complications"),
    ("endocr_02",    "endocrine_history",  "ICD-10-CM", "E66.9",  "Obesity, unspecified"),
    ("endocr_03",    "endocrine_history",  "ICD-10-CM", "E07.9",  "Disorder of thyroid, unspecified"),

    # ── Lung history (ICD-10-CM) ──────────────────────────────────────────
    ("zab_leg_01",   "lung_history",       "ICD-10-CM", "J42",    "Unspecified chronic bronchitis"),
    ("zab_leg_02",   "lung_history",       "ICD-10-CM", "J44.1",  "Chronic obstructive pulmonary disease with acute exacerbation"),
    ("zab_leg_03",   "lung_history",       "ICD-10-CM", "J45.901","Unspecified asthma, uncomplicated"),
    ("zab_leg_04",   "lung_history",       "ICD-10-CM", "J18.9",  "Pneumonia, unspecified organism"),
    ("zab_leg_06",   "lung_history",       "ICD-10-CM", "J81.1",  "Chronic pulmonary edema"),

    # ── Outcomes (ICD-10-CM + LOINC) ──────────────────────────────────────
    ("fibr_preds",   "outcomes",           "ICD-10-CM", "I48.91", "Unspecified atrial fibrillation (outcome — AF prediction target)"),
    ("fibr_preds",   "outcomes",           "LOINC",     "8893-0", "Heart rhythm (ECG) — AF classification"),
    ("preds_tah",    "outcomes",           "ICD-10-CM", "I47.1",  "Supraventricular tachycardia (outcome)"),
    ("jelud_tah",    "outcomes",           "ICD-10-CM", "I47.2",  "Ventricular tachycardia (outcome)"),
    ("fibr_jelud",   "outcomes",           "ICD-10-CM", "I49.01", "Ventricular fibrillation (outcome)"),
    ("a_v_blok",     "outcomes",           "ICD-10-CM", "I44.2",  "Atrioventricular block, complete (outcome)"),
    ("otek_lanc",    "outcomes",           "ICD-10-CM", "J81.0",  "Acute pulmonary edema (outcome)"),
    ("razriv",       "outcomes",           "ICD-10-CM", "I23.3",  "Rupture of cardiac wall without hemopericardium (outcome)"),
    ("dressler",     "outcomes",           "ICD-10-CM", "I24.1",  "Dressler syndrome (post-MI pericarditis)"),
    ("zsn",          "outcomes",           "ICD-10-CM", "I50.9",  "Heart failure, unspecified (outcome)"),
    ("rec_im",       "outcomes",           "ICD-10-CM", "I22.9",  "Subsequent MI of unspecified site (recurrent)"),
    ("p_im_sten",    "outcomes",           "ICD-10-CM", "I23.7",  "Postinfarction angina"),
    ("let_is",       "outcomes",           "ICD-10-CM", "I46.9",  "Cardiac arrest, cause unspecified (lethal outcome)"),
]

cur.executemany(
    """INSERT INTO clinical_codes
       (variable_name, table_name, code_system, code_value, code_description)
       VALUES (%s, %s, %s, %s, %s)""",
    CODES
)
print(f"  Inserted {len(CODES)} clinical code mappings.")

conn.commit()
cur.close()
conn.close()
print("\nMigration complete.")

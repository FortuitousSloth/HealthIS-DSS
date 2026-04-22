-- =========================================
-- DATABASE: Healthcare DSS (MI Patients)
-- =========================================

-- =========================
-- 0. PROVIDERS
-- =========================
CREATE TABLE providers (
    provider_id   SERIAL PRIMARY KEY,
    full_name     TEXT NOT NULL,
    specialty     TEXT NOT NULL DEFAULT 'Emergency Medicine'
);

-- =========================
-- 1. PATIENTS (Demographics)
-- =========================
CREATE TABLE patients (
    patient_id  INTEGER PRIMARY KEY,
    age         INTEGER,
    sex         INTEGER,
    provider_id INTEGER REFERENCES providers(provider_id)
);

-- =========================
-- 2. CARDIOVASCULAR HISTORY
-- =========================
CREATE TABLE cv_history (
    patient_id INTEGER PRIMARY KEY REFERENCES patients(patient_id),
    inf_anam INTEGER,
    stenok_an INTEGER,
    fk_stenok INTEGER,
    ibs_post INTEGER,
    ibs_nasl INTEGER,
    gb INTEGER,
    sim_gipert INTEGER,
    dlit_ag INTEGER,
    zsn_a INTEGER
);

-- =========================
-- 3. ARRHYTHMIA HISTORY (nr)
-- =========================
CREATE TABLE arrhythmia_history (
    patient_id INTEGER PRIMARY KEY REFERENCES patients(patient_id),
    nr11 INTEGER,
    nr01 INTEGER,
    nr02 INTEGER,
    nr03 INTEGER,
    nr04 INTEGER,
    nr07 INTEGER,
    nr08 INTEGER
);

-- =========================
-- 4. CONDUCTION HISTORY (np)
-- =========================
CREATE TABLE conduction_history (
    patient_id INTEGER PRIMARY KEY REFERENCES patients(patient_id),
    np01 INTEGER,
    np04 INTEGER,
    np05 INTEGER,
    np07 INTEGER,
    np08 INTEGER,
    np09 INTEGER,
    np10 INTEGER
);

-- =========================
-- 5. ENDOCRINE HISTORY
-- =========================
CREATE TABLE endocrine_history (
    patient_id INTEGER PRIMARY KEY REFERENCES patients(patient_id),
    endocr_01 INTEGER,
    endocr_02 INTEGER,
    endocr_03 INTEGER
);

-- =========================
-- 6. LUNG DISEASE HISTORY
-- =========================
CREATE TABLE lung_history (
    patient_id INTEGER PRIMARY KEY REFERENCES patients(patient_id),
    zab_leg_01 INTEGER,
    zab_leg_02 INTEGER,
    zab_leg_03 INTEGER,
    zab_leg_04 INTEGER,
    zab_leg_06 INTEGER
);

-- =========================
-- 7. ADMISSION VITALS
-- =========================
CREATE TABLE admission_vitals (
    patient_id INTEGER PRIMARY KEY REFERENCES patients(patient_id),
    s_ad_kbrig NUMERIC,
    d_ad_kbrig NUMERIC
);

-- =========================
-- 9. CLINICAL CODES (LOINC / ICD-10-CM reference)
-- =========================
CREATE TABLE clinical_codes (
    code_id          SERIAL PRIMARY KEY,
    variable_name    TEXT NOT NULL,
    table_name       TEXT NOT NULL,
    code_system      TEXT NOT NULL,   -- 'LOINC' or 'ICD-10-CM'
    code_value       TEXT NOT NULL,
    code_description TEXT NOT NULL
);

-- =========================
-- 8. OUTCOMES
-- =========================
CREATE TABLE outcomes (
    patient_id INTEGER PRIMARY KEY REFERENCES patients(patient_id),
    fibr_preds INTEGER,
    preds_tah INTEGER,
    jelud_tah INTEGER,
    fibr_jelud INTEGER,
    a_v_blok INTEGER,
    otek_lanc INTEGER,
    razriv INTEGER,
    dressler INTEGER,
    zsn INTEGER,
    rec_im INTEGER,
    p_im_sten INTEGER,
    let_is INTEGER
);
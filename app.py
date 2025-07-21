import streamlit as st
import openai
from openai import OpenAI

st.set_page_config(page_title="AIMA - Infection Management", layout="centered")
st.title("🧠 AIMA: AI Infection Management Assistant")
st.subheader("🩺 Multi-Syndrome Evaluation Tool")

st.markdown("---")

st.header("📋 Patient Data Input")
col1, col2 = st.columns(2)
with col1:
    age = st.number_input("Age", min_value=0, max_value=120, step=1)
with col2:
    sex = st.radio("Sex", ["Male", "Female", "Other"])

suspected_focus = st.selectbox(
    "Suspected Infection Focus (optional)",
    ["Unspecified", "Pulmonary", "Urinary", "Abdominal", "CNS", "Skin/Soft Tissue", "Bloodstream", "Other"]
)

focus_symptom_map = {
    "Pulmonary": ["Fever", "Chills", "Fatigue", "Productive cough", "Non-productive cough", "Shortness of breath", "Wheezing", "Chest pain"],
    "Urinary": ["Fever", "Chills", "Dysuria", "Urinary frequency", "Urinary urgency", "Purulent discharge", "Flank pain"],
    "Abdominal": ["Fever", "Chills", "Abdominal pain", "Nausea", "Vomiting", "Diarrhea"],
    "CNS": ["Fever", "Confusion", "Headache", "Vision changes", "Neck stiffness"],
    "Skin/Soft Tissue": ["Fever", "Chills", "Rash", "Erythema", "Leg swelling", "Warmth", "Drainage"],
    "Bloodstream": ["Fever", "Chills", "Fatigue", "Hypotension", "Confusion"],
    "Other": ["Fever", "Chills", "Fatigue"],
    "Unspecified": ["Fever", "Chills", "Fatigue"]
}

if "symptom_options" not in st.session_state:
    st.session_state.symptom_options = focus_symptom_map.get(suspected_focus, focus_symptom_map["Unspecified"])

if suspected_focus:
    st.session_state.symptom_options = focus_symptom_map.get(suspected_focus, focus_symptom_map["Unspecified"])

st.markdown("### Suggested Symptoms")
symptoms = st.multiselect("Select applicable symptoms:", options=st.session_state.symptom_options)

st.markdown("### Additional Symptoms")
additional_symptoms = st.text_area("List any additional symptoms not covered above")

st.markdown("**Vitals**")
col1, col2, col3 = st.columns(3)
with col1:
    temp = st.text_input("Temp (°C)")
    hr = st.text_input("Heart Rate (bpm)")
with col2:
    rr = st.text_input("Respiratory Rate (bpm)")
    bp = st.text_input("Blood Pressure (mmHg)")
with col3:
    o2 = st.text_input("O2 Sat (%)")

exam = st.text_area("Physical Exam Findings")

st.markdown("---")

st.header("📈 Scoring Tools")
if suspected_focus in ["Pulmonary", "Bloodstream"]:
    st.markdown("#### CURB-65")
    curb_confusion = st.checkbox("Confusion")
    curb_bun = st.text_input("BUN > 19 mg/dL (Yes/No)")
    curb_rr = st.text_input("RR ≥ 30 (Yes/No)")
    curb_bp = st.text_input("SBP < 90 or DBP ≤ 60 (Yes/No)")
    curb_age = age >= 65
    st.markdown(f"**CURB-65 Age Criteria:** {'Yes' if curb_age else 'No'}")

setting = st.selectbox("Patient Location", ["Outpatient", "ER", "Inpatient", "ICU"])

if setting in ["ER", "Inpatient", "ICU"]:
    st.markdown("#### qSOFA")
    qsofa_rr = st.text_input("RR ≥ 22 (Yes/No)")
    qsofa_altered = st.checkbox("Altered mental status")
    qsofa_sbp = st.text_input("SBP ≤ 100 mmHg (Yes/No)")

    st.markdown("#### SIRS Criteria")
    sirs_temp = st.text_input("Temp >38°C or <36°C (Yes/No)")
    sirs_hr = st.text_input("HR > 90 bpm (Yes/No)")
    sirs_rr = st.text_input("RR > 20 or PaCO₂ < 32 mmHg (Yes/No)")
    sirs_wbc = st.text_input("WBC > 12k or < 4k or >10% bands (Yes/No)")

st.markdown("---")
    
allergy_options = ["Penicillin", "Cephalosporins", "Macrolides", "Fluoroquinolones"]
allergies = st.multiselect("Allergies", options=allergy_options)
other_allergy = ""
if "Other" in allergies or st.checkbox("Other allergy not listed?"):
    other_allergy = st.text_input("Specify other allergy")

st.markdown("---")

st.header("📊 Labs & Imaging")
col1, col2 = st.columns(2)
with col1:
    wbc = st.text_input("WBC")
    procalcitonin = st.text_input("Procalcitonin")
    na = st.text_input("Sodium")
    k = st.text_input("Potassium")
    cl = st.text_input("Chloride")
    bicarb = st.text_input("Bicarbonate")
    bun = st.text_input("BUN")
    creatinine = st.text_input("Creatinine")
    glucose = st.text_input("Glucose")
with col2:
    ast = st.text_input("AST")
    alt = st.text_input("ALT")
    alp = st.text_input("ALP")
    tbili = st.text_input("Total Bilirubin")
    rpp = st.text_area("Respiratory Pathogen Panel (BioFire)")
    other_labs = st.text_area("Other Labs")
    cxr_summary = st.text_area("CXR / CT Summary")

st.subheader("🧪 Urinalysis")
leuk = st.text_input("Leukocyte Esterase")
nitrites = st.text_input("Nitrites")
urine_wbc = st.text_input("WBCs in urine")
squamous_cells = st.text_input("Squamous cells")
urine_culture = st.text_area("Urine Culture (with reflex)")

st.subheader("🧪 Body Fluid Culture")
fluid_source = st.selectbox("Fluid Collection Site", ["", "Pleural fluid", "Peritoneal fluid", "CSF", "Joint space"])
fluid_culture = st.text_area("Body Fluid Culture Results")

st.markdown("---")

st.header("🦠 Microbiologic History")
sputum = st.text_area("Previous Sputum Cultures")
resistant_orgs = st.text_area("Prior Resistant Organisms (if any)")

st.markdown("---")

st.header("📍 Setting")
setting = st.radio("Patient Location", ["Outpatient", "ER", "Inpatient", "ICU"])

st.markdown("---")

if st.button("🔘 Submit"):
    st.subheader("📡 AI Response")

    combined_symptoms = symptoms + ([s.strip() for s in additional_symptoms.split(',')] if additional_symptoms else [])

    # Compose prompt
    user_prompt = f"""
    A {age}-year-old {sex} presents with the following:

    Suspected infection focus: {suspected_focus}

    📝 Clinical Presentation:
    {', '.join(combined_symptoms)}

    🩺 Physical Exam:
    {exam}

    🧪 Lab Results:
    - WBC: {wbc}
    - Procalcitonin: {procalcitonin}
    - BMP: Na {na}, K {k}, Cl {cl}, Bicarb {bicarb}, BUN {bun}, Cr {creatinine}, Glucose {glucose}
    - Liver Enzymes: AST {ast}, ALT {alt}, ALP {alp}, Total Bili {tbili}
    - Respiratory Pathogen Panel (multiplex PCR): {rpp}
    - Urinalysis: LE {leuk}, Nitrites {nitrites}, WBCs {urine_wbc}, Squamous cells {squamous_cells}
    - Urine Culture: {urine_culture}
    - Body Fluid Culture from {fluid_source}: {fluid_culture}
    - Other labs: {other_labs}

    🖼️ Imaging Summary:
    {cxr_summary}

    🦠 Microbiologic History:
    - Previous Sputum Cultures: {sputum}
    - Prior Resistant Organisms: {resistant_orgs}

    ⚠️ Allergies:
    {', '.join(allergies)} {f"Other: {other_allergy}" if other_allergy else ""}

    🏥 Setting:
    {setting}

    ---

    Please:
    1. List the most likely infectious diagnoses with confidence level (e.g., high/moderate/low)
    2. Recommend empiric antibiotic therapy including drug, dose, and route
       - If the patient has a penicillin allergy, do NOT default to vancomycin or fluoroquinolones unless warranted
       - Consider cephalosporins in non-anaphylactic PCN allergies
       - Always follow IDSA guideline-based recommendations
    3. Flag any stewardship or safety concerns based on patient data
    4. List potential non-infectious differentials
    5. Provide up to 3 clickable guideline citations (IDSA preferred)
    6. Include a clinical disclaimer reminding the user to apply their judgment
    """

    try:
        # Load OpenAI client safely inside button action
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an infectious diseases assistant supporting infection syndrome diagnosis and treatment. Use IDSA guidelines where applicable. Evaluate for any infection syndrome, not just CAP. Adjust your assessment based on clinical setting (ED, outpatient, inpatient, ICU) and suspected site if given. Always remind the user that clinical discretion is essential."},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3
        )

 output = response.choices[0].message.content

# Insert section headers into the raw LLM response (if not already structured)
output = output.replace("1.", "### 🧠 Most Likely Infectious Diagnoses\n\n1.")
output = output.replace("2.", "### 💊 Empiric Antibiotic Recommendations\n\n2.")
output = output.replace("3.", "### 🛡️ Stewardship & Safety Concerns\n\n3.")
output = output.replace("4.", "### 🩺 Non-Infectious Differentials\n\n4.")
output = output.replace("5.", "### 📚 Guideline References\n\n5.")
output = output.replace("6.", "### ⚠️ Clinical Disclaimer\n\n6.")

st.markdown(output)

    except Exception as e:
        st.error(f"Error generating AI response: {e}")


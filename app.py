import streamlit as st
import openai
from openai import OpenAI
import pandas as pd
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import base64
import json

st.set_page_config(page_title="AIMA - Infection Management", layout="centered")
st.title("🧠 AIMA: AI Infection Management Assistant")
st.subheader("🩺 Multi-Syndrome Evaluation Tool")

st.markdown("---")

# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
gspread_json = base64.b64decode(st.secrets["GSPREAD_CREDENTIALS"]).decode("utf-8")
creds_dict = json.loads(gspread_json)
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client_gs = gspread.authorize(creds)
sheet = client_gs.open_by_key("1UJ6nTTKKzmbtuX8O1ggkCLxB6CU7BuPuy6H4bYwoTPw").sheet1

# Input UI begins
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

setting = st.selectbox("Patient Location", ["Outpatient", "ER", "Inpatient", "ICU"])

# Labs and imaging
wbc = st.text_input("WBC")
procalcitonin = st.text_input("Procalcitonin")
na = st.text_input("Sodium")
k = st.text_input("Potassium")
cl = st.text_input("Chloride")
bicarb = st.text_input("Bicarbonate")
bun = st.text_input("BUN")
creatinine = st.text_input("Creatinine")
glucose = st.text_input("Glucose")
ast = st.text_input("AST")
alt = st.text_input("ALT")
alp = st.text_input("ALP")
tbili = st.text_input("Total Bilirubin")
rpp = st.text_area("Respiratory Pathogen Panel (BioFire)")
other_labs = st.text_area("Other Labs")
cxr_summary = st.text_area("CXR / CT Summary")

# Microbiology and cultures
leuk = st.text_input("Leukocyte Esterase")
nitrites = st.text_input("Nitrites")
urine_wbc = st.text_input("WBCs in urine")
squamous_cells = st.text_input("Squamous cells")
urine_culture = st.text_area("Urine Culture (with reflex)")

fluid_source = st.selectbox("Fluid Collection Site", ["", "Pleural fluid", "Peritoneal fluid", "CSF", "Joint space"])
fluid_culture = st.text_area("Body Fluid Culture Results")

sputum = st.text_area("Previous Sputum Cultures")
resistant_orgs = st.text_area("Prior Resistant Organisms (if any)")

allergy_options = ["Penicillin", "Cephalosporins", "Macrolides", "Fluoroquinolones"]
allergies = st.multiselect("Allergies", options=allergy_options)
other_allergy = ""
if "Other" in allergies or st.checkbox("Other allergy not listed?"):
    other_allergy = st.text_input("Specify other allergy")

# Submit and process AI request
if st.button("🔘 Submit"):
    st.subheader("📡 AI Response")

    combined_symptoms = symptoms + ([s.strip() for s in additional_symptoms.split(',')] if additional_symptoms else [])

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
        st.markdown(output)

        st.markdown("---")
        st.header("📝 Clinician Feedback")
        usefulness = st.radio("Was this output clinically useful?", ["Yes", "Somewhat", "No"])
        errors = st.text_area("Were there any inaccuracies or safety concerns?")
        suggestions = st.text_area("How could this tool be improved?")

        if st.button("Submit Feedback"):
            feedback_row = [
                datetime.now().isoformat(),
                age,
                sex,
                suspected_focus,
                ", ".join(combined_symptoms),
                exam,
                output,
                usefulness,
                errors,
                suggestions
            ]
            sheet.append_row(feedback_row)
            st.success("✅ Feedback submitted to Google Sheets. Thank you!")

    except Exception as e:
        st.error(f"Error generating AI response: {e}")

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

suggested_symptoms = focus_symptom_map.get(suspected_focus, focus_symptom_map["Unspecified"])

st.markdown("### Suggested Symptoms")
symptoms = st.multiselect("Select applicable symptoms:", options=suggested_symptoms)

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
    bmp = st.text_area("Basic Metabolic Panel (BMP)")
    lfts = st.text_area("Liver Enzymes (AST/ALT/ALP/Tbili)")
    blood_cultures = st.text_area("Blood Cultures")
with col2:
    rpp = st.text_area("Respiratory Pathogen Panel (BioFire)")
    other_labs = st.text_area("Other Labs")
    cxr_summary = st.text_area("CXR / CT Summary")

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
    - BMP: {bmp}
    - Liver Enzymes: {lfts}
    - Respiratory Pathogen Panel (multiplex PCR): {rpp}
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

        st.markdown(response.choices[0].message.content)

    except Exception as e:
        st.error(f"Error generating AI response: {e}")

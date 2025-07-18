import streamlit as st
import openai
from openai import OpenAI

# Initialize OpenAI client using Streamlit secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
st.write("Key loaded:", "OPENAI_API_KEY" in st.secrets)

st.set_page_config(page_title="AIMA - CAP Module", layout="centered")
st.title("🧠 AIMA: AI Infection Management Assistant")
st.subheader("🚨 Community-Acquired Pneumonia (CAP) Module")

st.markdown("---")

st.header("📋 Patient Data Input")
col1, col2 = st.columns(2)
with col1:
    age = st.number_input("Age", min_value=0, max_value=120, step=1)
with col2:
    sex = st.radio("Sex", ["Male", "Female", "Other"])

symptoms = st.multiselect(
    "Symptoms",
    [
        "Productive cough", "Non-productive cough", "Fever", "Chills",
        "Shortness of breath", "Wheezing", "Chest pain", "Fatigue"
    ]
)

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
    blood_cultures = st.text_area("Blood Cultures")
with col2:
    rpp = st.text_area("Respiratory Pathogen Panel (BioFire)")
    cxr_summary = st.text_area("CXR / CT Summary")

st.markdown("---")

st.header("🦠 Microbiologic History")
sputum = st.text_area("Previous Sputum Cultures")
resistant_orgs = st.text_area("Prior Resistant Organisms (if any)")

st.markdown("---")

st.header("📍 Setting")
setting = st.radio("Patient Location", ["Outpatient", "ER", "Inpatient"])

st.markdown("---")

if st.button("🔘 Submit"):
    st.subheader("📡 AI Response")

    # Compose prompt
    user_prompt = f"""
    A {age}-year-old {sex} presents with {', '.join(symptoms)}.

    Vitals: Temp {temp}, HR {hr}, RR {rr}, BP {bp}, O2 Sat {o2}
    Physical exam: {exam}
    PMH: {setting}
    Allergies: {', '.join(allergies)} {f"Other: {other_allergy}" if other_allergy else ""}

    Labs:
    - WBC: {wbc}
    - Procalcitonin: {procalcitonin}
    - Blood Cultures: {blood_cultures}
    - Respiratory Pathogen Panel: {rpp}
    - Imaging: {cxr_summary}

    Microbiology:
    - Previous Sputum Cultures: {sputum}
    - Prior Resistant Organisms: {resistant_orgs}

    Please:
    1. Estimate CURB-65 score
    2. Provide diagnosis confidence
    3. Recommend empiric antibiotics (dose + duration)
    4. Flag stewardship/safety concerns
    5. Suggest differentials
    6. Include disclaimer
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an infectious diseases assistant supporting CAP management. Use IDSA/ATS guidelines and always remind the user that clinical discretion is essential."},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3
        )

        st.markdown(response.choices[0].message.content)

    except Exception as e:
        st.error(f"Error generating AI response: {e}")


import streamlit as st
import pandas as pd
import joblib
import matplotlib.pyplot as plt

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="TutoringMaster",
    page_icon="🎓",
    layout="wide"
)

model = joblib.load("model.pkl")

st.title("🎓 TutoringMaster")
st.markdown("### Student Performance Prediction System")

st.divider()

# =========================
# LABEL MAPS
# =========================
gender_map = {"Male": 0, "Female": 1}
ethnicity_map = {
    "Caucasian": 0,
    "African American": 1,
    "Asian": 2,
    "Other": 3
}
parent_edu_map = {
    "None": 0,
    "High School": 1,
    "Some College": 2,
    "Bachelor's": 3,
    "Higher": 4
}
binary_map = {"No": 0, "Yes": 1}
support_map = {
    "No": 0,
    "Low": 1,
    "Moderate": 2,
    "High": 3
}

# =========================
# SIDEBAR
# =========================
st.sidebar.title("📚 Student Information")

def user_input():

    age = st.sidebar.slider("Age", 15, 18, 17)

    gender = st.sidebar.selectbox("Gender", list(gender_map.keys()))
    ethnicity = st.sidebar.selectbox("Ethnicity", list(ethnicity_map.keys()))
    parent_edu = st.sidebar.selectbox("Parental Education", list(parent_edu_map.keys()))

    study = st.sidebar.slider("Study Time Weekly", 0.0, 25.0, 10.0)
    absences = st.sidebar.slider("Absences", 0, 30, 5)

    tutoring = st.sidebar.selectbox("Tutoring", list(binary_map.keys()))
    parental_support = st.sidebar.selectbox("Parental Support", list(support_map.keys()))

    extracurricular = st.sidebar.selectbox("Extracurricular", list(binary_map.keys()))
    sports = st.sidebar.selectbox("Sports", list(binary_map.keys()))
    music = st.sidebar.selectbox("Music", list(binary_map.keys()))
    volunteering = st.sidebar.selectbox("Volunteering", list(binary_map.keys()))

    return pd.DataFrame([{
        "Age": age,
        "Gender": gender_map[gender],
        "Ethnicity": ethnicity_map[ethnicity],
        "ParentalEducation": parent_edu_map[parent_edu],
        "StudyTimeWeekly": study,
        "Absences": absences,
        "Tutoring": binary_map[tutoring],
        "ParentalSupport": support_map[parental_support],
        "Extracurricular": binary_map[extracurricular],
        "Sports": binary_map[sports],
        "Music": binary_map[music],
        "Volunteering": binary_map[volunteering]
    }])

input_data = user_input()

# =========================
# DISPLAY
# =========================
col1, col2 = st.columns(2)

with col1:
    st.subheader("📋 Student Data")
    st.dataframe(input_data, width='stretch')

with col2:
    st.subheader("📊 Key Indicators")
    st.metric("Study Hours", input_data["StudyTimeWeekly"][0])
    st.metric("Absences", input_data["Absences"][0])
    st.metric("Parental Support", input_data["ParentalSupport"][0])

st.divider()

# =========================
# PREDICTION
# =========================
if st.button("Predict Grade Class"):

    prediction = model.predict(input_data)[0]

    st.subheader("🎯 Result")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Predicted GradeClass", prediction)

    with col2:
        risk = "High" if prediction in [3, 4] else "Low"
        st.metric("Risk Level", risk)

    # =========================
    # PROBABILITY
    # =========================
    if hasattr(model, "predict_proba"):
        probs = model.predict_proba(input_data)[0]

        prob_df = pd.DataFrame({
            "Class": model.classes_,
            "Probability": probs
        })

        st.subheader("📈 Prediction Confidence")

        fig, ax = plt.subplots()
        ax.bar(prob_df["Class"], prob_df["Probability"])
        ax.set_ylabel("Probability")

        st.pyplot(fig)

    # =========================
    # RECOMMENDATIONS
    # =========================
    st.subheader("💡 Recommendations")

    recs = []

    if input_data["Absences"][0] > 10:
        recs.append("Reduce absences to improve performance.")

    if input_data["StudyTimeWeekly"][0] < 5:
        recs.append("Increase weekly study time.")

    if input_data["ParentalSupport"][0] == 0:
        recs.append("Lack of parental support may affect performance.")

    if len(recs) == 0:
        st.success("Student profile looks strong!")
    else:
        for r in recs:
            st.warning(r)
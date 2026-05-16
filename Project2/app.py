import streamlit as st
import pandas as pd
import joblib

# Load model
model = joblib.load("model.pkl")

st.title("🎓 TutoringMaster - Performance Predictor")

st.sidebar.header("Student Input")

def user_input():
    age = st.sidebar.selectbox("Age", ["18", "19-22", "23-27"])
    sex = st.sidebar.selectbox("Sex", ["Male", "Female"])
    high_school = st.sidebar.selectbox("High School Type", ["State", "Private", "Other"])
    scholarship = st.sidebar.selectbox("Scholarship", ["0%", "25%", "50%", "75%", "100%"])
    additional_work = st.sidebar.selectbox("Additional Work", ["Yes", "No"])
    sports = st.sidebar.selectbox("Sports Activity", ["Yes", "No"])
    transport = st.sidebar.selectbox("Transportation", ["Bus", "Private"])
    study_hours = st.sidebar.slider("Weekly Study Hours", 0, 20, 5)
    attendance = st.sidebar.selectbox("Attendance", ["Always", "Sometimes", "Never"])
    reading = st.sidebar.selectbox("Reading", ["Yes", "No"])
    notes = st.sidebar.selectbox("Notes", ["Yes", "No"])
    listening = st.sidebar.selectbox("Listening", ["Yes", "No"])
    project = st.sidebar.selectbox("Project Work", ["Yes", "No"])

    return pd.DataFrame([[
        age, sex, high_school, scholarship,
        additional_work, sports, transport,
        study_hours, attendance, reading,
        notes, listening, project
    ]], columns=[
        "Student_Age", "Sex", "High_School_Type", "Scholarship",
        "Additional_Work", "Sports_activity", "Transportation",
        "Weekly_Study_Hours", "Attendance", "Reading",
        "Notes", "Listening_in_Class", "Project_work"
    ])

input_data = user_input()

st.write("### Input Data")
st.write(input_data)

if st.button("Predict Grade"):
    prediction = model.predict(input_data)[0]
    st.success(f"Predicted Grade: {prediction}")
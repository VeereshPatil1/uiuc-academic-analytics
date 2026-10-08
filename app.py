import pandas as pd
import streamlit as st

from gpa import semester_summary

st.set_page_config(page_title="UIUC Academic Analytics", page_icon="🎓", layout="wide")

st.title("UIUC Academic Analytics Dashboard")
st.write("Track your courses, GPA, and academic trends.")

# Load the data and run the GPA math
df = pd.read_csv("data/sample_courses.csv")
summary = semester_summary(df)
latest = summary.iloc[-1]

# How much did cumulative GPA change since the previous semester?
if len(summary) > 1:
    change = latest["cumulative_gpa"] - summary.iloc[-2]["cumulative_gpa"]
    gpa_delta = f"{change:+.2f} since last semester"
else:
    gpa_delta = None

# Headline numbers in 4 side-by-side columns
col1, col2, col3, col4 = st.columns(4)
col1.metric("🎓 Cumulative GPA", f"{latest['cumulative_gpa']:.2f}", gpa_delta)
col2.metric("📚 Total Credits", int(latest["cumulative_credits"]))
col3.metric("📝 Courses", len(df))
col4.metric("🗓️ Semesters", len(summary))
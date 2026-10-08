import pandas as pd
import streamlit as st

from charts import (
    credits_by_semester_chart,
    gpa_by_department_chart,
    gpa_over_time_chart,
    grade_distribution_chart,
)
from gpa import department_summary, semester_summary

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

st.divider()

# Charts in a 2 x 2 grid
left, right = st.columns(2)
left.plotly_chart(gpa_over_time_chart(summary), width="stretch")
right.plotly_chart(credits_by_semester_chart(summary), width="stretch")

left, right = st.columns(2)
left.plotly_chart(grade_distribution_chart(df), width="stretch")
right.plotly_chart(gpa_by_department_chart(department_summary(df)), width="stretch")
import math

import pandas as pd
import streamlit as st

from charts import (
    credits_by_semester_chart,
    gpa_by_department_chart,
    gpa_over_time_chart,
    grade_distribution_chart,
)
from gpa import GRADE_POINTS, department_summary, projected_gpa, required_gpa, semester_summary

# Semester choices for the dropdown: Spring 2022, Summer 2022, Fall 2022, ... Fall 2030
SEMESTERS = [f"{term} {year}" for year in range(2022, 2031) for term in ["Spring", "Summer", "Fall"]]


def empty_courses():
    """An empty courses table with the right columns and types."""
    return pd.DataFrame({
        "semester": pd.Series(dtype="str"),
        "course": pd.Series(dtype="str"),
        "department": pd.Series(dtype="str"),
        "credits": pd.Series(dtype="float"),
        "grade": pd.Series(dtype="str"),
    })


def replace_courses(new_courses):
    """Swap in a new set of courses and give the table a fresh start."""
    st.session_state.courses = new_courses
    st.session_state.editor_version += 1


st.set_page_config(page_title="UIUC Academic Analytics", page_icon="🎓", layout="wide")

# --- Memory: runs only the very first time the page loads ---
if "courses" not in st.session_state:
    st.session_state.courses = empty_courses()
    st.session_state.editor_version = 0

st.title("UIUC Academic Analytics Dashboard")
st.write("Track your courses, GPA, and academic trends.")

# --- Sidebar buttons ---
with st.sidebar:
    st.header("Data")
    if st.button("📂 Load sample data", width="stretch"):
        replace_courses(pd.read_csv("data/sample_courses.csv"))
    if st.button("🗑️ Clear all courses", width="stretch"):
        replace_courses(empty_courses())

# --- Editable course table ---
st.subheader("Your Courses")
st.caption("Click a cell to edit. Add rows at the bottom. To delete, select a row's checkbox and click the trash icon.")
edited = st.data_editor(
    st.session_state.courses,
    key=f"editor_{st.session_state.editor_version}",
    num_rows="dynamic",
    hide_index=True,
    width="stretch",
    column_config={
        "semester": st.column_config.SelectboxColumn("Semester", options=SEMESTERS, required=True),
        "course": st.column_config.TextColumn("Course", required=True),
        "department": st.column_config.TextColumn("Department", required=True),
        "credits": st.column_config.NumberColumn("Credits", min_value=1, max_value=10, step=1, format="%d", required=True),
        "grade": st.column_config.SelectboxColumn("Grade", options=list(GRADE_POINTS), required=True),
    },
)

# Only use rows where every column is filled in
df = edited.dropna()
if df.empty:
    st.info("Add your courses above, or click **Load sample data** in the sidebar to try it out.")
    st.stop()

# --- GPA math (used by both tabs) ---
summary = semester_summary(df)
latest = summary.iloc[-1]
current_gpa = latest["cumulative_gpa"]

if len(summary) > 1:
    change = current_gpa - summary.iloc[-2]["cumulative_gpa"]
    gpa_delta = f"{change:+.2f} since last semester"
else:
    gpa_delta = None

st.divider()

dashboard_tab, whatif_tab = st.tabs(["Dashboard", "What-If"])

with dashboard_tab:
    # --- Headline numbers ---
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Cumulative GPA", f"{current_gpa:.2f}", gpa_delta)
    col2.metric("Total Credits", int(latest["cumulative_credits"]))
    col3.metric("Courses", len(df))
    col4.metric("Semesters", len(summary))

    st.divider()

    # --- Charts in a 2 x 2 grid ---
    left, right = st.columns(2)
    left.plotly_chart(gpa_over_time_chart(summary), width="stretch")
    right.plotly_chart(credits_by_semester_chart(summary), width="stretch")

    left, right = st.columns(2)
    left.plotly_chart(grade_distribution_chart(df), width="stretch")
    right.plotly_chart(gpa_by_department_chart(department_summary(df)), width="stretch")

with whatif_tab:
    # --- What-if calculator ---
    st.subheader("What-If Calculator")
    st.write("Plan next semester's courses and the grades you expect, and see what happens to your GPA.")

    starter_plan = pd.DataFrame({
        "course": ["Course 1", "Course 2", "Course 3", "Course 4"],
        "credits": [3, 3, 4, 4],
        "grade": ["A", "A-", "B+", "A"],
    })
    planned = st.data_editor(
        starter_plan,
        key="planned_editor",
        num_rows="dynamic",
        hide_index=True,
        width="stretch",
        column_config={
            "course": st.column_config.TextColumn("Course (optional)"),
            "credits": st.column_config.NumberColumn("Credits", min_value=1, max_value=10, step=1, format="%d", required=True),
            "grade": st.column_config.SelectboxColumn("Expected Grade", options=list(GRADE_POINTS), required=True),
        },
    )
    planned = planned.dropna(subset=["credits", "grade"])

    if planned.empty:
        st.info("Add at least one planned course to see your projected GPA.")
    else:
        new_gpa = projected_gpa(df, planned)
        col1, col2, col3 = st.columns(3)
        col1.metric("Current GPA", f"{current_gpa:.2f}")
        col2.metric("Projected GPA", f"{new_gpa:.2f}", f"{new_gpa - current_gpa:+.2f}")
        col3.metric("Planned Credits", int(planned["credits"].sum()))

    # --- Goal mode ---
    st.divider()
    st.subheader("Goal Mode")
    st.write("Pick a target GPA and see what you'd need next semester to reach it.")

    col1, col2 = st.columns(2)
    target = col1.number_input("Target cumulative GPA", min_value=0.0, max_value=4.0, value=3.6, step=0.05)
    next_credits = col2.number_input("Credits next semester", min_value=1, max_value=30, value=15, step=1)

    needed = required_gpa(df, target, next_credits)

    if needed > 4.0:
        best_case = projected_gpa(df, pd.DataFrame({"credits": [next_credits], "grade": ["A"]}))
        # Round DOWN so we never overstate the best possible GPA (3.6483 -> 3.64, not 3.65)
        best_case = math.floor(best_case * 100) / 100
        st.error(
            f"A {target:.2f} isn't reachable next semester with {next_credits} credits. "
            f"Even straight A's would bring you to {best_case:.2f}."
        )
    elif needed <= 0:
        st.success(f"You're already set! Your cumulative GPA will stay at or above {target:.2f} no matter what.")
    else:
        # Find the lowest letter grade that meets the requirement
        for letter in reversed(GRADE_POINTS):
            if GRADE_POINTS[letter] >= needed:
                break
        st.info(
            f"You need a **{needed:.2f}** GPA over your next {next_credits} credits "
            f"(roughly a **{letter}** average) to reach a {target:.2f}."
        )
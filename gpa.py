import pandas as pd
# UIUC grade scale: letter grade -> grade points
GRADE_POINTS = {
    "A+": 4.00, "A": 4.00, "A-": 3.67,
    "B+": 3.33, "B": 3.00, "B-": 2.67,
    "C+": 2.33, "C": 2.00, "C-": 1.67,
    "D+": 1.33, "D": 1.00, "D-": 0.67,
    "F": 0.00,
}


def grade_to_points(grade):
    """Convert a letter grade (like 'A-') to grade points (like 3.67)."""
    cleaned = grade.strip().upper()
    if cleaned not in GRADE_POINTS:
        valid = ", ".join(GRADE_POINTS)
        raise ValueError(f"'{grade}' is not a valid grade. Use one of: {valid}")
    return GRADE_POINTS[cleaned]

# Order of terms within a year (Spring comes first)
TERM_ORDER = {"Spring": 1, "Summer": 2, "Fall": 3}


def semester_sort_key(semester):
    """Turn 'Fall 2024' into a number that sorts in time order (20243)."""
    parts = semester.strip().split()
    if len(parts) != 2 or parts[0].capitalize() not in TERM_ORDER or not parts[1].isdigit():
        raise ValueError(f"'{semester}' is not a valid semester. Use a format like 'Fall 2024'.")
    term = parts[0].capitalize()
    year = int(parts[1])
    return year * 10 + TERM_ORDER[term]

def add_gpa_columns(df):
    """Return a copy of the courses table with grade points, quality points, and a semester sort key."""
    df = df.copy()
    df["grade_points"] = df["grade"].apply(grade_to_points)
    df["quality_points"] = df["grade_points"] * df["credits"]
    df["semester_key"] = df["semester"].apply(semester_sort_key)
    # "stable" keeps courses in their original order within the same semester
    return df.sort_values("semester_key", kind="stable")

def semester_summary(df):
    """One row per semester with total credits, course count, and semester GPA."""
    courses = add_gpa_columns(df)
    summary = courses.groupby(["semester_key", "semester"], as_index=False).agg(
        credits=("credits", "sum"),
        courses=("course", "count"),
        quality_points=("quality_points", "sum"),
    )
    summary["semester_gpa"] = summary["quality_points"] / summary["credits"]
    summary["cumulative_credits"] = summary["credits"].cumsum()
    summary["cumulative_gpa"] = summary["quality_points"].cumsum() / summary["cumulative_credits"]
    return summary

def department_summary(df):
    """One row per department with total credits, course count, and department GPA (highest first)."""
    courses = add_gpa_columns(df)
    summary = courses.groupby("department", as_index=False).agg(
        credits=("credits", "sum"),
        courses=("course", "count"),
        quality_points=("quality_points", "sum"),
    )
    summary["gpa"] = summary["quality_points"] / summary["credits"]
    return summary.sort_values("gpa", ascending=False, kind="stable")

def projected_gpa(df, planned):
    """Cumulative GPA after adding planned courses (a table with 'credits' and 'grade' columns)."""
    current = add_gpa_columns(df)
    planned_points = planned["grade"].apply(grade_to_points) * planned["credits"]
    total_points = current["quality_points"].sum() + planned_points.sum()
    total_credits = current["credits"].sum() + planned["credits"].sum()
    if total_credits == 0:
        return None
    return total_points / total_credits


def required_gpa(df, target_gpa, next_credits):
    """GPA needed over the next `next_credits` credits to reach `target_gpa` cumulative."""
    if next_credits <= 0:
        raise ValueError("Next semester credits must be greater than 0.")
    current = add_gpa_columns(df)
    current_points = current["quality_points"].sum()
    current_credits = current["credits"].sum()
    needed_points = target_gpa * (current_credits + next_credits) - current_points
    return needed_points / next_credits

REQUIRED_COLUMNS = ["semester", "course", "department", "credits", "grade"]


def clean_courses(df):
    """Check a courses table and tidy it up. Raises ValueError with a helpful message if something is wrong."""
    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(
            f"Missing column(s): {', '.join(missing)}. "
            f"Your file needs these columns: {', '.join(REQUIRED_COLUMNS)}."
        )

    df = df[REQUIRED_COLUMNS].dropna().copy()

    # Tidy text so "cs" and " CS " count as the same department
    df["semester"] = df["semester"].astype(str).str.strip().str.title()
    df["course"] = df["course"].astype(str).str.strip().str.upper()
    df["department"] = df["department"].astype(str).str.strip().str.upper()
    df["grade"] = df["grade"].astype(str).str.strip().str.upper()

    df["credits"] = pd.to_numeric(df["credits"], errors="coerce")
    if df["credits"].isna().any() or (df["credits"] <= 0).any():
        raise ValueError("Every course needs a credits value that is a number greater than 0.")

    # These raise a clear ValueError if any grade or semester is invalid
    df["grade"].apply(grade_to_points)
    df["semester"].apply(semester_sort_key)

    return df
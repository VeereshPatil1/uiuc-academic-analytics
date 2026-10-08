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
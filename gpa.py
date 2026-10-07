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
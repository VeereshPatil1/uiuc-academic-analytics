import pandas as pd
import pytest

from gpa import grade_to_points, semester_sort_key, semester_summary


def test_a_plus_counts_same_as_a():
    assert grade_to_points("A+") == 4.0
    assert grade_to_points("A") == 4.0


def test_grade_input_is_cleaned():
    assert grade_to_points(" b+ ") == 3.33


def test_invalid_grade_raises_error():
    with pytest.raises(ValueError):
        grade_to_points("Z")


def test_semesters_sort_in_time_order():
    semesters = ["Spring 2026", "Fall 2024", "Fall 2025", "Spring 2025"]
    expected = ["Fall 2024", "Spring 2025", "Fall 2025", "Spring 2026"]
    assert sorted(semesters, key=semester_sort_key) == expected


def test_cumulative_gpa_is_weighted_by_credits():
    # 1 credit of A + 16 credits of C should be 36/17 (about 2.12), NOT the simple average 3.0
    df = pd.DataFrame({
        "semester": ["Fall 2024", "Spring 2025"],
        "course": ["CS 100", "MATH 221"],
        "department": ["CS", "MATH"],
        "credits": [1, 16],
        "grade": ["A", "C"],
    })
    summary = semester_summary(df)
    assert summary["cumulative_gpa"].iloc[-1] == pytest.approx(36 / 17)
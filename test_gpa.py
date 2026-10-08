import pandas as pd
import pytest

from gpa import (
    department_summary,
    grade_to_points,
    projected_gpa,
    required_gpa,
    semester_sort_key,
    semester_summary,
)

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


def test_department_gpa_is_weighted_by_credits():
    df = pd.DataFrame({
        "semester": ["Fall 2024", "Fall 2024", "Fall 2024"],
        "course": ["CS 124", "CS 100", "MATH 221"],
        "department": ["CS", "CS", "MATH"],
        "credits": [3, 1, 4],
        "grade": ["A", "C", "B"],
    })
    summary = department_summary(df).set_index("department")
    # CS: (4.0*3 + 2.0*1) / 4 credits = 3.5
    assert summary.loc["CS", "gpa"] == pytest.approx(3.5)
    assert summary.loc["MATH", "gpa"] == pytest.approx(3.0)

def test_projected_gpa_adds_planned_courses():
    df = pd.DataFrame({
        "semester": ["Fall 2024"],
        "course": ["CS 124"],
        "department": ["CS"],
        "credits": [4],
        "grade": ["B"],
    })
    planned = pd.DataFrame({"credits": [4], "grade": ["A"]})
    # (3.0*4 + 4.0*4) / 8 credits = 3.5
    assert projected_gpa(df, planned) == pytest.approx(3.5)


def test_required_gpa_to_reach_target():
    df = pd.DataFrame({
        "semester": ["Fall 2024"],
        "course": ["CS 124"],
        "department": ["CS"],
        "credits": [4],
        "grade": ["C"],
    })
    # Current: 2.0 over 4 credits. To reach 3.0 over 8 total credits,
    # you need 24 total points - 8 current = 16 points over 4 credits = 4.0
    assert required_gpa(df, target_gpa=3.0, next_credits=4) == pytest.approx(4.0)
    
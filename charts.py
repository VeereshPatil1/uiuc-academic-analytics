import plotly.express as px
import plotly.express as px

from gpa import GRADE_POINTS
# Main chart color (a clear, colorblind-friendly blue)
BLUE = "#2a78d6"
ORANGE = "#eb6834"


def credits_by_semester_chart(summary):
    """Bar chart of total credits taken each semester."""
    fig = px.bar(
        summary,
        x="semester",
        y="credits",
        title="Credits by Semester",
        labels={"semester": "Semester", "credits": "Credits"},
    )
    fig.update_traces(marker_color=BLUE)
    fig.update_layout(template="plotly_white")
    return fig

def gpa_over_time_chart(summary):
    """Line chart of semester GPA and cumulative GPA over time."""
    data = summary.rename(columns={
        "semester_gpa": "Semester GPA",
        "cumulative_gpa": "Cumulative GPA",
    })
    fig = px.line(
        data,
        x="semester",
        y=["Semester GPA", "Cumulative GPA"],
        markers=True,
        title="GPA Over Time",
        labels={"semester": "Semester", "value": "GPA", "variable": ""},
        color_discrete_sequence=[BLUE, ORANGE],
    )
    fig.update_traces(line_width=2, marker_size=8, hovertemplate="%{y:.2f}")
    fig.update_layout(template="plotly_white", hovermode="x unified")
    return fig

def grade_distribution_chart(df):
    """Bar chart of how many courses got each letter grade, best grade first."""
    grades = df["grade"].str.strip().str.upper()
    counts = grades.value_counts()
    order = [grade for grade in GRADE_POINTS if grade in counts.index]
    counts = counts.reindex(order).reset_index()
    fig = px.bar(
        counts,
        x="grade",
        y="count",
        title="Grade Distribution",
        labels={"grade": "Grade", "count": "Courses"},
    )
    fig.update_traces(marker_color=BLUE)
    fig.update_layout(template="plotly_white")
    fig.update_yaxes(dtick=1)
    return fig
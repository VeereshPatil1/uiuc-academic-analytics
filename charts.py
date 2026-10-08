import plotly.express as px

# Main chart color (a clear, colorblind-friendly blue)
BLUE = "#2a78d6"


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
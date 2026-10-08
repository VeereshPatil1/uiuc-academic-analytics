import pandas as pd
from gpa import semester_summary
from charts import grade_distribution_chart

df = pd.read_csv("data/sample_courses.csv")
summary = semester_summary(df)

fig = grade_distribution_chart(df)
fig.show()
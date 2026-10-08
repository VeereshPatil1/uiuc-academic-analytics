import pandas as pd
from gpa import semester_summary
from charts import credits_by_semester_chart

df = pd.read_csv("data/sample_courses.csv")
summary = semester_summary(df)

fig = credits_by_semester_chart(summary)
fig.show()
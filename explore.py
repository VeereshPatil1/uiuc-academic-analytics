import pandas as pd
from gpa import semester_summary
from charts import gpa_over_time_chart

df = pd.read_csv("data/sample_courses.csv")
summary = semester_summary(df)

fig = gpa_over_time_chart(summary)
fig.show()
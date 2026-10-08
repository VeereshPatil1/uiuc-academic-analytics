import pandas as pd
from gpa import department_summary
from charts import gpa_by_department_chart

df = pd.read_csv("data/sample_courses.csv")

fig = gpa_by_department_chart(department_summary(df))
fig.show()
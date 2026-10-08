import pandas as pd
from gpa import semester_summary

df = pd.read_csv("data/sample_courses.csv")
print(semester_summary(df).round(2))
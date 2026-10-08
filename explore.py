import pandas as pd
from gpa import add_gpa_columns

df = pd.read_csv("data/sample_courses.csv")
courses = add_gpa_columns(df)

print(courses.head(8))
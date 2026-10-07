import pandas as pd

# Read the CSV file into a DataFrame (a table)
df = pd.read_csv("data/sample_courses.csv")

print("First 5 rows:")
print(df.head())

print("\nRows and columns:")
print(df.shape)

print("\nColumn types:")
print(df.dtypes)

print("\nTotal credits:")
print(df["credits"].sum())

print("\nNumber of courses:")
print(len(df))

print("\nCourses per department:")
print(df["department"].value_counts())

print("\nOnly CS courses:")
print(df[df["department"] == "CS"])

print("\nCredits per semester:")
print(df.groupby("semester")["credits"].sum())
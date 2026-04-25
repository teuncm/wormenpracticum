import pandas as pd

df = pd.read_csv("data/0-5v_125000Hz_80ms.csv")

first_column = df.iloc[:, 0]
second_column = df.iloc[:, 1]

df.iloc[:, 0] = second_column
df.iloc[:, 1] = first_column

df.to_csv("data/0-5v_125000Hz_80ms_swapped.csv", index=False)

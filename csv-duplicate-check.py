import pandas as pd

df = pd.read_csv('/path/your/csv/the.csv')

duplicate_rows = df[df.duplicated(keep=False)]

print("Duplicate Rows based on All Values:")
print(duplicate_rows)

if not duplicate_rows.empty:
    melted_df = pd.melt(df)

    duplicate_values = melted_df[melted_df.duplicated(keep=False)]

    print("\nRows with Duplicate Values:")
    print(duplicate_values)
else:
    print("\nNo duplicate rows based on all values.")


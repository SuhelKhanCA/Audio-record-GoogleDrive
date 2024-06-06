import pandas as pd

# Read the text files
df1 = pd.read_csv('train_ENG.txt', delimiter = "\t")
df2 = pd.read_csv('train_HIN.txt', delimiter = "\t")

# Reset the index to create an ID column
df1.reset_index(inplace=True)
df2.reset_index(inplace=True)

# Rename the columns
df1.columns = ['ID', 'Data1']
df2.columns = ['ID', 'Data2']

# Merge the dataframes on the ID column
merged_df = pd.merge(df1, df2, on='ID')

# Save the merged dataframe as an Excel file
merged_df.to_excel('merged.xlsx', index=False)

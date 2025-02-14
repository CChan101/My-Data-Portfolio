import pandas as pd

pd.set_option('display.max_columns', None)  # Show all columns
pd.set_option('display.width', 1000)  # Set a wide display width

# Download the database you sent me and read it
df = pd.read_csv("processed_final_2.csv")
df.rename(columns={df.columns[0]: 'txid'}, inplace=True)
print(df.head())

# For the graph, get the transaction ID, entry block, entry time, timestamp, and confirmation time (timestamp - entry time)
new_df = df[['txid', 'EntryBlock', 'EntryTime']].copy()

# Move the new df to a new csv
new_df.to_csv('cut_processed_final.csv')

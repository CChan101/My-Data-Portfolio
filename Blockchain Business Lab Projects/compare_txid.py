import pandas as pd
import requests
import matplotlib.pyplot as plt

pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', None)  # Show all columns
df_cut = pd.read_csv("cut_processed_final.csv")
timestamps = []
confirmation_time = []

#Set df_cut.head(100) for testing

#Create an algorithm to parse through unique_entry_blocks
# Iterate through rows of the DataFrame
for index, row in df_cut.iterrows():
    block_height = row['EntryBlock']

    # Step 1: Get Block Hash
    block_hash_url = f"https://mempool.space/api/block-height/{block_height}"
    block_hash_response = requests.get(block_hash_url)

    block_hash = block_hash_response.text.strip()

    # Step 2: Get Block Details
    block_details_url = f"https://mempool.space/api/block/{block_hash}"
    block_details_response = requests.get(block_details_url)

    block_details = block_details_response.json()

    # Extract Timestamp
    timestamp = block_details.get('timestamp')

    # Append Timestamp
    timestamps.append(timestamp)

    # Calculate Confirmation Time
    entry_time = row['EntryTime']
    confirm_time = timestamp - entry_time
    confirmation_time.append(confirm_time)


#Add timestamp and confirmation time
df_cut['Timestamp'] = timestamps
df_cut['Confirmation Time'] = confirmation_time
df_cut['Difference'] = df_cut['EntryTime'] - df_cut['Confirmation Time']

#Create a histogram
df_cut['Difference'].hist(grid=False, color='blue', edgecolor='black', rwidth=0.8)
plt.xlabel('Difference (EntryTime - ConfTime)')
plt.ylabel('Frequency')
plt.title('Histogram')
plt.show()
print(df_cut.head(100))
import pandas as pd

# Load the data
df = pd.read_csv('test.csv')

# Strip and normalize columns
df.columns = df.columns.str.strip()
df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
df['Description'] = df['Description'].str.strip()

# Add type column
df['Type'] = df['Amount'].apply(lambda x: 'Income' if x > 0 else 'Expense')

import json
import os

CATEGORY_FILE = 'category_map.json'

# Load existing description-to-category map
if os.path.exists(CATEGORY_FILE):
    with open(CATEGORY_FILE, 'r') as f:
        category_map = json.load(f)
else:
    category_map = {}

# Ask user to categorize unknown descriptions
for desc in df['Description'].unique():
    if desc not in category_map:
        print(f"\n❓ New Description Detected:\n'{desc}'")
        category = input("Enter a category for this description (e.g. 'Groceries', 'Transport', 'Salary'): ")
        category_map[desc] = category

# Save updated category map
with open(CATEGORY_FILE, 'w') as f:
    json.dump(category_map, f, indent=2)

# Apply category to the DataFrame
df['Category'] = df['Description'].map(category_map)

summary = df.groupby(['Category', 'Type'])['Amount'].sum().unstack(fill_value=0)
print("\n📊 Summary by Category:")
print(summary)
# Save the categorized DataFrame
df.to_csv('bank_categorized.csv', index=False)
# Save the summary to a CSV file
summary.to_csv('bank_summary.csv')
# Save the summary to a JSON file
summary.to_json('bank_summary.json', orient='records', indent=2)
# Save the categorized DataFrame to a JSON file
df.to_json('bank_categorized.json', orient='records', indent=2)

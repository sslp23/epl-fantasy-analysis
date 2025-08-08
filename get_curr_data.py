import pandas as pd
import requests

s = '2025-26'
url = 'https://fantasy.premierleague.com/api/bootstrap-static/'

response = requests.get(url)
data = response.json()

df = pd.json_normalize(data['elements'])

# Add season column
df['season'] = s

# Select and reorder columns
columns_to_keep = ['code', 'minutes', 'points_per_game', 'web_name', 'team_code', 'element_type', 'season']
df = df[columns_to_keep]


# Rename id to code to match historical data
#df.rename(columns={'id': 'code'}, inplace=True)
df.to_csv(f'curr_data/{s}_data.csv', index=False)
import pandas as pd

s = '2025-26'
df = pd.read_csv(f'https://raw.githubusercontent.com/vaastav/Fantasy-Premier-League/refs/heads/master/data/{s}/players_raw.csv')

df.to_csv(f'curr_data/{s}_data.csv')
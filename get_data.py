import pandas as pd

seasons = ['2016-17', '2017-18', '2018-19', '2019-20', '2020-21', '2021-22', '2022-23', '2023-24',
           '2024-25']

for s in seasons:
    df = pd.read_csv(f'https://raw.githubusercontent.com/vaastav/Fantasy-Premier-League/refs/heads/master/data/{s}/players_raw.csv')

    df.to_csv(f'history_data/{s}_data.csv')
import pandas as pd

df_19_20 = pd.read_html("https://www.ffstuff.co.uk/playersFPL201920.php")[0]

df_20_21 = pd.read_html("https://www.ffstuff.co.uk/playersFPL202021.php")[0]

df_19_20.to_csv('history_data/fpl_19_20.csv', index=False)
df_20_21.to_csv('history_data/fpl_20_21.csv', index=False)
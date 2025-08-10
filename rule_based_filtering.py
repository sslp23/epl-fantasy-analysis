import pandas as pd

def apply_filters(data, filters_columns = [], filters_values = [], relationships = []):
    data_filtered = data.copy()

    if len(filters_columns) != len(filters_values):
        raise ValueError("The length of columns and values must be the same.")

    for i, column in enumerate(filters_columns):
        value = filters_values[i]
        relationship = relationships[i]
        
        if relationship == '>':
            data_filtered = data_filtered[data_filtered[column] > value]
        elif relationship == '<':
            data_filtered = data_filtered[data_filtered[column] < value]
        elif relationship == '>=':
            data_filtered = data_filtered[data_filtered[column] >= value]
        elif relationship == '<=':
            data_filtered = data_filtered[data_filtered[column] <= value]
        elif relationship == '==':
            data_filtered = data_filtered[data_filtered[column] == value]
        elif relationship == '!=':
            data_filtered = data_filtered[data_filtered[column] != value]
        elif relationship == 'in':
            data_filtered = data_filtered[data_filtered[column].isin(value)]
        elif relationship == 'not in':
            data_filtered = data_filtered[~data_filtered[column].isin(value)]

    return data_filtered

def write_tiers_to_excel(tiers, filename='player_tiers.xlsx'):
    """
    Writes a list of DataFrames to an Excel file, each in a separate sheet.
    Adjusts column widths to fit the content.

    Args:
        tiers (list): A list of pandas DataFrames.
        filename (str): The name of the Excel file to create.
    """
    with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
        for i, df in enumerate(tiers):
            sheet_name = f'Tier {i+1}'
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            worksheet = writer.sheets[sheet_name]
            for j, col in enumerate(df.columns):
                # find length of column header and data
                column_len = max((df[col].astype(str).map(len).max()), len(str(col)))
                # set column width
                worksheet.set_column(j, j, column_len + 2)

def main():
    data = pd.read_csv('25_26_data_parsed.csv')
    data = data[data['Player Name'] != 'Luis Díaz']

    data.sort_values('minutes_last_season', ascending=False)[['team_code', 'Player Name']].drop_duplicates('team_code')

    team_mapper = {3: 'Arsenal', 11: 'Everton', 94: 'Brentford', 54: 'Fulham', 17: 'Nottingham Forest', 
                   31: 'Crystal Palace', 1: 'Manchester United', 14: 'Liverpool', 8: 'Chelsea',
                   21: 'West Ham', 4: 'Newcastle', 43: 'Manchester City', 36: 'Brighton',
                   91: 'Bournemouth', 7: 'Aston Villa', 2: 'Leeds United', 6: 'Tottenham',
                   56: 'Sunderland', 90: 'Burnley', 39: 'Wolverhampton'}

    position_mapper = {1: 'GK', 2:'DEF', 3:'MID', 4:'FWD'}
    data['Position Name'] = data.Position.map(position_mapper)
    data['Team Name'] = data.team_code.map(team_mapper)

    # First tier filtering:
    filter_cols = ['New In Team', 'points_last_season', 'avg_points_last_2_seasons', 'avg_minutes_last_2_seasons']

    filter_vals = [False, 4.4, 5.35, 1736]

    relationship = ['==', '>=', '>=', '>=']
    filtered_data = apply_filters(data, filters_columns=filter_cols, filters_values=filter_vals, relationships = relationship)
    top_tier = filtered_data.copy()

    # Filters for T2
    # First, FWDs
    # I'll build a T2 premium for FWDs 
    # They are players with thresholds above the 2nd quartile for the past season and past 2 seasons
    filter_vals = [False, 4.1, 4.2, 1736]
    data_filt = data[~data.ID.isin(top_tier.ID.unique())]

    relationship = ['==', '>=', '>=', '>=']
    filtered_data = apply_filters(data_filt[data_filt.Position == 4], filters_columns=filter_cols, filters_values=filter_vals, relationships = relationship)
    tier2_fwd_premium = filtered_data.copy()
    manual_adjustments = ['Wood', 'Wissa', 'Havertz']
    # Removing manual adjustments -> this group will have only Mateta after manual adjustments
    tier2_fwd_premium = tier2_fwd_premium[~tier2_fwd_premium['Player Name'].isin(manual_adjustments)]

    # Now, full tier 2
    data_filt = data_filt[~data_filt.ID.isin(tier2_fwd_premium.ID.unique())]
    relationship = ['==', '>=', '>=', '>=']
    filter_vals = [False, 3.575, 3.125, 1736]

    filtered_data = apply_filters(data_filt[data_filt.Position == 4], filters_columns=filter_cols, filters_values=filter_vals, relationships = relationship)
    tier2_fwd = filtered_data.copy()
    
    manual_adjustments = ['N.Jackson', 'Havertz']
    # Removing manual adjustments -> this group will have only Mateta after manual adjustments
    tier2_fwd = tier2_fwd[~tier2_fwd['Player Name'].isin(manual_adjustments)]

    # MIDs
    filter_cols = ['New In Team', 'points_last_season', 'avg_points_last_2_seasons', 'minutes_last_season']
    filter_vals = [False, 4.2, 3.9, 2454]

    relationship = ['==', '>=', '>=', '>=']
    filtered_data = apply_filters(data_filt[data_filt.Position == 3], filters_columns=filter_cols, filters_values=filter_vals, relationships = relationship)
    tier2_mid = filtered_data.copy()

    # DEFs
    filter_vals = [False, 3.9, 3.85, 1200]
    relationship = ['==', '>=', '>=', '>=']
    filtered_data = apply_filters(data_filt[data_filt.Position == 2], filters_columns=filter_cols, filters_values=filter_vals, relationships = relationship)
    tier2_def = filtered_data.copy()
    
    # Manual Adjustments
    tier2_def = pd.concat([tier2_def, data_filt[data_filt['Player Name'] == 'Virgil']])
    tier2_full = pd.concat([tier2_fwd_premium, tier2_fwd, tier2_def, tier2_mid])
    tier2_full
    data_filt = data_filt[~data_filt.ID.isin(tier2_full.ID.values)]

    # With tier 2 ready, I'll go to tier 3. Let's start by analysing GKs
    filter_vals = [False, 3.95, 1200]
    relationship = ['==', '>=', '>=']
    filter_cols = ['New In Team', 'avg_points_last_2_seasons', 'minutes_last_season']
    
    filtered_data = apply_filters(data_filt[data_filt.Position == 1], filters_columns=filter_cols, filters_values=filter_vals, relationships = relationship)
    tier3_gk = filtered_data.copy()
    tier3_gk

    # Midfielders - New In Team
    filter_vals = [True, 3.125, 2170.5]
    relationship = ['==', '>=', '>=']
    filter_cols = ['New In Team', 'avg_points_last_2_seasons', 'minutes_last_season']
    
    filtered_data = apply_filters(data_filt[data_filt.Position == 3], filters_columns=filter_cols, filters_values=filter_vals, relationships = relationship)
    tier3_mid_new = filtered_data.copy()

    # Midfielders - All Premium
    filter_vals = [False, 3.85, 3.95, 2314.5]
    relationship = ['==', '>=', '>=', '>=']
    filter_cols = ['New In Team', 'points_last_season', 'avg_points_last_2_seasons', 'minutes_last_season']
    
    filtered_data = apply_filters(data_filt[data_filt.Position == 3], filters_columns=filter_cols, filters_values=filter_vals, relationships = relationship)
    tier3_mid_premium = filtered_data.copy()
    manual_adjustments = ['Trossard'] # high competition
    tier3_mid_premium = tier3_mid_premium[~tier3_mid_premium['Player Name'].isin(manual_adjustments)]
    data_filt = data_filt[~data_filt['Player Name'].isin(tier3_mid_premium['Player Name'])]
    
    #Midfielders - All
    filter_vals = [False, 3.2, 3.2, 1878]
    relationship = ['==', '>=', '>=', '>=']
    filter_cols = ['New In Team', 'points_last_season', 'avg_points_last_2_seasons', 'minutes_last_season']
    
    filtered_data = apply_filters(data_filt[data_filt.Position == 3], filters_columns=filter_cols, filters_values=filter_vals, relationships = relationship)
    tier3_mid_all = filtered_data.copy()
    
    tier3_mid = pd.concat([tier3_mid_premium, tier3_mid_all, tier3_mid_new])
    len(tier3_mid)+len(tier3_gk)+len(tier2_full)+len(top_tier)

    # FWDs 
    filter_vals = [False, 0, 4, 2182.0]
    relationship = ['==', '>=', '>=', '>=']
    filter_cols = ['New In Team', 'points_last_season', 'avg_points_last_2_seasons', 'avg_minutes_last_2_seasons']
    
    filtered_data = apply_filters(data_filt[data_filt.Position == 4], filters_columns=filter_cols, filters_values=filter_vals, relationships = relationship)
    tier3_fwd_old = filtered_data
    tier3_fwd_old

    # FWDs - new

    # FWDs 
    filter_vals = [True, 2.8, 3.55, 1754]
    relationship = ['==', '>=', '>=', '>=']
    filter_cols = ['New In Team', 'points_last_season', 'avg_points_last_2_seasons', 'minutes_last_season']
    
    filtered_data = apply_filters(data_filt[data_filt.Position == 4], filters_columns=filter_cols, filters_values=filter_vals, relationships = relationship)
    tier3_fwd_new = filtered_data
    tier3_fwd_new
    
    tier3_fwd = pd.concat([tier3_fwd_new, tier3_fwd_old])
    
    # DEFs
    filter_vals = [False, 3.2, 3.0125, 1400]
    relationship = ['==', '>=', '>=', '>=']
    filter_cols = ['New In Team', 'points_last_season', 'avg_points_last_2_seasons', 'minutes_last_season']

    filtered_data = apply_filters(data_filt[data_filt.Position == 2], filters_columns=filter_cols, filters_values=filter_vals, relationships = relationship)
    tier3_def = filtered_data.copy()
    tier3_def

    tier3_full = pd.concat([tier3_fwd, tier3_def, tier3_gk, tier3_mid])

    len(top_tier)+len(tier2_full)+len(tier3_full)
    data_filt = data_filt[~data_filt.ID.isin(tier3_full.ID.values)]

    # Tier 4 players
    # GKs, MIDs and DEFs have some options, so I'll work with lowering thresholds
    # FWDs -> trying to find good PPG in lower mins played

    # DEFs -> new in team players
    filter_vals = [True, 3, 0, 2266.0]
    relationship = ['==', '>=', '>=', '>=']
    filter_cols = ['New In Team', 'points_last_season', 'avg_points_last_2_seasons', 'avg_minutes_last_2_seasons']

    filtered_data = apply_filters(data_filt[data_filt.Position == 2], filters_columns=filter_cols, filters_values=filter_vals, relationships = relationship)
    tier4_def_new = filtered_data.copy()

    # DEFs -> not new  in team players
    filter_vals = [False, 3, 0, 1500.0]
    relationship = ['==', '>=', '>=', '>=']
    filter_cols = ['New In Team', 'points_last_season', 'avg_points_last_2_seasons', 'avg_minutes_last_2_seasons']

    filtered_data = apply_filters(data_filt[data_filt.Position == 2], filters_columns=filter_cols, filters_values=filter_vals, relationships = relationship)
    tier4_def = filtered_data.copy()
    manual_adjustments = ['Burn', 'Colwill']
    tier4_def = tier4_def[~tier4_def['Player Name'].isin(manual_adjustments)]
    tier4_def = pd.concat([tier4_def, tier4_def_new])

    # MIDs
    filter_vals = [False, 3.1, 0, 1813.0]
    relationship = ['==', '>=', '>=', '>=']
    filter_cols = ['New In Team', 'points_last_season', 'avg_points_last_2_seasons', 'minutes_last_season']

    filtered_data = apply_filters(data_filt[data_filt.Position == 3], filters_columns=filter_cols, filters_values=filter_vals, relationships = relationship)
    tier4_mid = filtered_data.copy()
    tier4_mid

    # FWDs
    filter_vals = [3.05, 0, 1195.0]
    relationship = ['>=', '>=', '>=']
    filter_cols = [ 'points_last_season', 'avg_points_last_2_seasons', 'minutes_last_season']

    filtered_data = apply_filters(data_filt[data_filt.Position == 4], filters_columns=filter_cols, filters_values=filter_vals, relationships = relationship)
    tier4_fwd = filtered_data.copy()
    tier4_fwd = tier4_fwd[~tier4_fwd['Player Name'].isin(['Foster'])]
    

    # GKs
    filter_vals = [False, 3.4, 0, 2500.0]
    relationship = ['==', '>=', '>=', '>=']
    filter_cols = ['New In Team', 'points_last_season', 'avg_points_last_2_seasons', 'minutes_last_season']

    filtered_data = apply_filters(data_filt[data_filt.Position == 1], filters_columns=filter_cols, filters_values=filter_vals, relationships = relationship)
    tier4_gk = filtered_data.copy()
    tier4_full = pd.concat([tier4_gk, tier4_def,tier4_mid,tier4_fwd])

    #Tier 5 - last tier before entering the filter by initial schedule
    # Starting with DEFs
    data_filt = data_filt[~data_filt.ID.isin(tier4_full.ID.values)]
    filter_vals = [False, 0, 2.8, 2690.0]
    relationship = ['==', '>=', '>=', '>=']
    filter_cols = ['New In Team', 'points_last_season', 'avg_points_last_2_seasons', 'avg_minutes_last_2_seasons']

    filtered_data = apply_filters(data_filt[data_filt.Position == 2], filters_columns=filter_cols, filters_values=filter_vals, relationships = relationship)
    tier5_def = filtered_data.copy()
    tier5_def

    # Tier 5 - Mid - Players with Experience
    filter_vals = [False, 2, 2.9, 1500]
    relationship = ['==', '>=', '>=', '>=']
    filter_cols = ['New In Team', 'time_in_league', 'avg_points_last_2_seasons', 'avg_minutes_last_2_seasons']

    filtered_data = apply_filters(data_filt[data_filt.Position == 3], filters_columns=filter_cols, filters_values=filter_vals, relationships = relationship)
    tier5_mid_old = filtered_data.copy()
    manual_adjustments = ['Maddison', 'Bailey']
    tier5_mid_old = tier5_mid_old[~tier5_mid_old['Player Name'].isin(manual_adjustments)]
    tier5_mid_old

    # Tier 5 - Mid - Players with low Experience
    data_filt = data_filt[~data_filt.ID.isin(tier5_mid_old.ID.values)]
    filter_vals = [False, 2, 3, 1000]
    relationship = ['==', '<=', '>=', '>=']
    filter_cols = ['New In Team', 'time_in_league', 'points_last_season', 'minutes_last_season']

    filtered_data = apply_filters(data_filt[data_filt.Position == 3], filters_columns=filter_cols, filters_values=filter_vals, relationships = relationship)
    tier5_mid_new = filtered_data.copy()
    
    tier5_mid = pd.concat([tier5_mid_new, tier5_mid_old])
    
    # Tier 5 GKs
    filter_vals = [False, 0, 3., 2000.0]
    relationship = ['==', '>=', '>=', '>=']
    filter_cols = ['New In Team', 'points_last_season', 'avg_points_last_2_seasons', 'minutes_last_season']

    filtered_data = apply_filters(data_filt[data_filt.Position == 1], filters_columns=filter_cols, filters_values=filter_vals, relationships = relationship)
    tier5_gk = filtered_data.copy()
    manual_adjustments = ['Ederson M.', 'José Sá']
    tier5_gk = tier5_gk[~tier5_gk['Player Name'].isin(manual_adjustments)]

    tier5_full = pd.concat([tier5_def, tier5_mid, tier5_gk])

    # Tier 6 - Players New In league
    # Here it works like a bonus tier
    # As shown, new in league players are a very risky group
    # The idea is to find players who will be replacements for good players in the past season

    filter_vals = [True, True, 2.5]
    relationship = ['==', '==', '>=', '>=']
    filter_cols = ['New In League', 'influential_player_left', 'max_ppg_in_team_position_last_season']

    filtered_data = apply_filters(data_filt, filters_columns=filter_cols, filters_values=filter_vals, relationships = relationship)
    bonus_tier = filtered_data.copy()
    bonus_tier['Notes'] = len(bonus_tier)*[' ']

    cols = ['ID', 'Player Name', 'Position Name', 'Team Name', 'points_last_season', 'avg_points_last_2_seasons', 'minutes_last_season', 'Notes']

    bonus_tier.drop('points_last_season', axis=1, inplace=True)
    bonus_tier.rename(columns = {'max_ppg_in_team_position_last_season': 'points_last_season'}, inplace=True)
    bonus_tier = bonus_tier[cols]

    tiers = [top_tier, tier2_full, tier3_full, tier4_full, tier5_full, bonus_tier]

    new_tiers = []


    for t in tiers:
        t['Notes'] = ['']*len(t)
        t = t[cols]
        new_tiers.append(t)

    write_tiers_to_excel(new_tiers)


if __name__ == '__main__':
    main()
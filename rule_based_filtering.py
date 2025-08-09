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

def main():
    data = pd.read_csv('25_26_data_parsed.csv')
    data = data[data['Player Name'] != 'Luis Díaz']

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





    
    #data_filt[data_filt['Player Name'].str.contains('Georginio')]


if __name__ == '__main__':
    main()
import pandas as pd
import numpy as np

def load_data():
    cols_to_use = ['code', 'minutes', 'points_per_game', 'web_name', 'team_code', 'element_type', 'season']
    
    df = pd.read_csv('curr_data/2025-26_data.csv')
    
    df['season'] = ['2025-26']*len(df)
    df = df[cols_to_use]
    df.rename(columns={
        'code': 'ID',
        'web_name': 'Player Name',
        'element_type': 'Position',
        'points_per_game': 'PPG',
        'minutes': 'Min'
    }, inplace=True)

    return df

def calculate_new_in_league(current_season_df, past_seasons_df):
    """
    Calculates the 'New In League' feature for each player for the current season.
    """
    last_season = past_seasons_df['season'].max()
    players_in_last_season = past_seasons_df[past_seasons_df['season'] == last_season]['ID'].unique()
    
    current_season_df['New In League'] = ~current_season_df['ID'].isin(players_in_last_season)
    
    return current_season_df

def calculate_new_in_team(current_season_df, past_seasons_df):
    """
    Calculates the 'New In Team' feature for each player for the current season.
    """
    last_season = past_seasons_df['season'].max()
    last_season_df = past_seasons_df[past_seasons_df['season'] == last_season]

    last_season_teams = last_season_df[['ID', 'team_code']].drop_duplicates(subset=['ID']).set_index('ID')['team_code']
    
    current_season_df['previous_team_code'] = current_season_df['ID'].map(last_season_teams)
    
    current_season_df['New In Team'] = (current_season_df['previous_team_code'].isnull()) | \
                                       (current_season_df['team_code'] != current_season_df['previous_team_code'])
    
    current_season_df.drop(columns=['previous_team_code'], inplace=True)

    return current_season_df

def calculate_additional_features(df):
    """
    Calculates additional features based on past season data.
    - max_minutes_in_position_past_season: For new players in a team, the max minutes
      played by anyone in that position in that team last season.
    - max_minutes_by_signing_past_season: For existing players, the max minutes
      played by a new signing in that team last season.
    - time_in_league: Number of previous seasons the player has been in the league.
    """
    # Sort by ID and season to ensure correct historical calculations
    df_sorted = df.sort_values(['ID', 'season']).reset_index(drop=True)
    
    # --- Feature 3: time_in_league ---
    # Easiest to calculate first. cumcount gives 0 for the first appearance, 1 for second, etc.
    df_sorted['time_in_league'] = df_sorted.groupby('ID').cumcount()
    
    # Get unique seasons and create a mapping from a season to its previous one
    seasons = sorted(df_sorted['season'].unique())
    season_map = {season: prev_season for season, prev_season in zip(seasons[1:], seasons[:-1])}
    
    # Create a 'previous_season' column to merge on
    df_sorted['previous_season'] = df_sorted['season'].map(season_map)

    # --- Feature 1: max_minutes_in_position_past_season ---
    # Pre-calculate max minutes per team/position for all seasons
    max_min_pos = df_sorted.groupby(['season', 'team_code', 'Position'])['Min'].max().reset_index()
    max_min_pos.rename(columns={'Min': 'max_minutes_in_position_past_season', 'season': 'previous_season'}, inplace=True)
    
    # Merge this data into the main dataframe
    df_with_features = pd.merge(
        df_sorted,
        max_min_pos,
        how='left',
        left_on=['previous_season', 'team_code', 'Position'],
        right_on=['previous_season', 'team_code', 'Position']
    )
    # Set the value to NaN if the player is not new in the team
    df_with_features['max_minutes_in_position_past_season'] = df_with_features['max_minutes_in_position_past_season'].where(df_with_features['New In Team'], np.nan)

    # --- Feature 2: max_minutes_by_signing_past_season ---
    # Get all new signings from all seasons
    new_signings = df_sorted[df_sorted['New In Team'] == True]
    # Calculate the max minutes for these signings per team and season
    max_min_signings = new_signings.groupby(['season', 'team_code'])['Min'].max().reset_index()
    max_min_signings.rename(columns={'Min': 'max_minutes_by_signing_past_season', 'season': 'previous_season'}, inplace=True)

    # Merge this data into the main dataframe
    df_with_features = pd.merge(
        df_with_features,
        max_min_signings,
        how='left',
        left_on=['previous_season', 'team_code'],
        right_on=['previous_season', 'team_code']
    )
    # Set the value to NaN if the player is not an existing player
    df_with_features['max_minutes_by_signing_past_season'] = df_with_features['max_minutes_by_signing_past_season'].where(df_with_features['New In Team'] == False, np.nan)

    # Clean up helper column
    df_with_features.drop(columns=['previous_season'], inplace=True)
    
    return df_with_features

def calculate_historical_features(df):
    """
    Calculates historical performance metrics for each player.
    This includes:
    - PPG from prior seasons (last 1, avg last 2, avg last 3).
    - Minutes played in prior seasons (last 1, avg last 2, avg last 3).
    - Minutes played in prior seasons for the *same team* as the current season.
    Args:
        df (pd.DataFrame): The DataFrame with player data for all seasons.
    Returns:
        pd.DataFrame: The DataFrame with all historical columns added.
    """
    df_sorted = df.sort_values(by=['ID', 'season'])

    def calculate_player_history(group):
        # Ensure the group is sorted by season for correct shifting and rolling
        group = group.sort_values('season')

        # --- Historical PPG ---
        shifted_ppg = group['PPG'].shift(1)
        group['points_last_season'] = shifted_ppg
        group['avg_points_last_2_seasons'] = shifted_ppg.rolling(2, min_periods=1).mean()
        group['avg_points_last_3_seasons'] = shifted_ppg.rolling(3, min_periods=1).mean()

        # --- Historical Minutes (Overall) ---
        shifted_min = group['Min'].shift(1)
        group['minutes_last_season'] = shifted_min
        group['avg_minutes_last_2_seasons'] = shifted_min.rolling(2, min_periods=1).mean()
        group['avg_minutes_last_3_seasons'] = shifted_min.rolling(3, min_periods=1).mean()

        # --- Historical Minutes (Same Team) ---
        same_team_hist_data = []
        # Iterate through each row (season) of the player's history
        for index, row in group.iterrows():
            current_season = row['season']
            current_team = row['team_code']

            # Get all seasons for this player *before* the current one
            history = group[group['season'] < current_season]

            # From that history, get only the seasons played at the *same team*
            same_team_history = history[history['team_code'] == current_team].sort_values('season', ascending=False)

            # Calculate metrics based on this filtered, same-team history
            if not same_team_history.empty:
                min_last = same_team_history.head(1)['Min'].iloc[0]
                # Use .mean() which handles cases with fewer than 2 or 3 seasons gracefully
                avg_min_2 = same_team_history.head(2)['Min'].mean()
                avg_min_3 = same_team_history.head(3)['Min'].mean()
            else:
                # If no history with this team, all metrics are NaN
                min_last, avg_min_2, avg_min_3 = np.nan, np.nan, np.nan

            same_team_hist_data.append({
                'index': index,
                'minutes_last_season_same_team': min_last,
                'avg_minutes_last_2_seasons_same_team': avg_min_2,
                'avg_minutes_last_3_seasons_same_team': avg_min_3
            })

        # Join the calculated same-team history back to the group
        if same_team_hist_data:
            same_team_df = pd.DataFrame(same_team_hist_data).set_index('index')
            group = group.join(same_team_df)

        return group

    # Apply the complex calculation to each player group
    df_with_hist = df_sorted.groupby('ID', group_keys=False).apply(calculate_player_history)

    return df_with_hist

def calculate_new_in_league_features(current_season_df, past_seasons_df):
    """
    Calculates features for players who are new to the league.
    - max_ppg_in_team_position_last_season: Max PPG in the same team/position last season.
    - influential_player_left: True if a player with >3 PPG and >1500 mins left the team.
    """
    if 'New In League' not in current_season_df.columns:
        return current_season_df

    position_mapper = {1: 'GK', 2: 'DEF', 3: 'MID', 4: 'FWD'}
    current_season_df['Position Name'] = current_season_df['Position'].map(position_mapper)

    last_season_name = sorted(past_seasons_df['season'].unique())[-1]
    last_season_df = past_seasons_df[past_seasons_df['season'] == last_season_name].copy()
    last_season_df['Position Name'] = last_season_df['Position']#.map(position_mapper)

    # Feature 1: Max PPG in team/position last season
    max_ppg_last_season = last_season_df[last_season_df.Min > 1500].groupby(['team_code', 'Position Name'])['PPG'].max().reset_index()
    max_ppg_last_season.rename(columns={'PPG': 'max_ppg_in_team_position_last_season'}, inplace=True)

    current_season_df = pd.merge(
        current_season_df,
        max_ppg_last_season,
        how='left',
        on=['team_code', 'Position Name']
    )
    current_season_df['max_ppg_in_team_position_last_season'] = current_season_df['max_ppg_in_team_position_last_season'].where(current_season_df['New In League'], np.nan)

    # Feature 2: Influential player left the team
    influential_players = last_season_df[((last_season_df['PPG'] > 3) & (last_season_df['Min'] > 1500)) | ((last_season_df['Min'] > 2300))]
    current_player_teams = current_season_df.set_index('ID')['team_code']
    influential_players['current_team_code'] = influential_players['ID'].map(current_player_teams)
    influential_left = influential_players[
        (influential_players['current_team_code'] != influential_players['team_code']) |
        (influential_players['current_team_code'].isnull())
    ]
    teams_and_positions_that_lost_player = influential_left[['team_code', 'Position Name']].drop_duplicates()
    
    current_season_df['influential_player_left'] = current_season_df.apply(
        lambda row: tuple(row[['team_code', 'Position Name']]) in set(map(tuple, teams_and_positions_that_lost_player.to_numpy())),
        axis=1
    )
    current_season_df['influential_player_left'] = current_season_df['influential_player_left'].where(current_season_df['New In League'], np.nan)

    return current_season_df


def main():
    df = load_data()

    past_data = pd.read_csv('fantasy_data_history.csv', usecols=['Player Name', 'ID', 'PPG', 'season', 'Min', 'team_code', 'New In Team', 'Position'])
    
    df = calculate_new_in_league(df, past_data)
    df = calculate_new_in_team(df, past_data)
    
    df = calculate_new_in_league_features(df, past_data)

    # For historical features, we combine, calculate, and then filter
    combined_data = pd.concat([past_data, df], ignore_index=True)
    combined_data = calculate_additional_features(combined_data)
    data_with_hist = calculate_historical_features(combined_data)
    
    # Filter for the current season
    current_season_data = data_with_hist[data_with_hist['season'] == '2025-26'].copy()
    
    current_season_data.to_csv('25_26_data_parsed.csv', index=False)
    '''
    ftier = current_season_data[(current_season_data.avg_points_last_2_seasons > 5) & (current_season_data.points_last_season > 5)]
    current_season_data[(current_season_data.avg_points_last_2_seasons > 4.4) & (current_season_data.points_last_season > 4.4) & (current_season_data.minutes_last_season > 1200) & (~current_season_data.ID.isin(ftier.ID.values.tolist()))]

    current_season_data[(current_season_data.avg_points_last_2_seasons > 4.1) & (current_season_data.points_last_season > 4.1) & (~current_season_data.ID.isin(ftier.ID.values.tolist()))]
    current_season_data[(current_season_data.avg_points_last_2_seasons > 3.5) & (current_season_data.points_last_season > 4.1) & (current_season_data.minutes_last_season > 1200) & (~current_season_data.ID.isin(ftier.ID.values.tolist()))]

    current_season_data[current_season_data['Player Name'] == 'Ødegaard']
    '''
if __name__ == '__main__':
    main()


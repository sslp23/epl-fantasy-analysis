import pandas as pd
import glob
import os
import numpy as np

def load_data():
    """
    Loads all player data from CSV files in the history_data directory,
    selects specific columns, and adds a 'season' column based on the filename.

    Returns:
        pandas.DataFrame: A single DataFrame containing all historical data.
    """
    path = 'history_data'
    all_files = glob.glob(os.path.join(path, "*_data.csv"))
    
    li = []
    
    cols_to_use = ['code', 'minutes', 'points_per_game', 'total_points', 'birth_date', 'web_name', 'team_code', 'team_join_date', 'element_type']

    for filename in all_files:
        df = pd.read_csv(filename, index_col=None, header=0, encoding='utf-8-sig')
        df.columns = df.columns.str.replace('"', '') # Clean column names

        # Extract season from filename
        season = os.path.basename(filename).split('_data.csv')[0]
        df['season'] = season
        
        # Ensure all requested columns are present, fill missing with NaN
        for col in cols_to_use:
            if col not in df.columns:
                df[col] = pd.NA

        # Select only the required columns
        df = df[cols_to_use + ['season']]
        
        li.append(df)

    frame = pd.concat(li, axis=0, ignore_index=True)
    
    # Rename to old column names
    frame.rename(columns={
        'code': 'ID',
        'web_name': 'Player Name',
        'element_type': 'Position',
        'total_points': 'Tot Pts',
        'points_per_game': 'PPG',
        'minutes': 'Min'
    }, inplace=True)
    
    positions = {1: 'GK', 2: 'DEF', 3: 'MID', 4: 'FWD'}
    frame['Position'] = frame.Position.map(positions)
    return frame

def calculate_new_in_league(df):
    """
    Calculates the 'New In League' feature for each player.

    A player is considered 'New In League' if they were not in the league
    in the previous season.

    Args:
        df (pd.DataFrame): The DataFrame with player data for all seasons.

    Returns:
        pd.DataFrame: The DataFrame with the 'New In League' column added.
    """
    df_sorted = df.sort_values('season').reset_index(drop=True)
    seasons = df_sorted['season'].unique()
    
    df_list = []

    # For the first season, 'New In League' is False for everyone
    first_season_df = df_sorted[df_sorted['season'] == seasons[0]].copy()
    first_season_df['New In League'] = False
    df_list.append(first_season_df)

    # Iterate from the second season
    for i in range(1, len(seasons)):
        previous_season = seasons[i-1]
        current_season = seasons[i]
        
        players_in_previous_season = df_sorted[df_sorted['season'] == previous_season]['ID'].unique()
        
        current_season_df = df_sorted[df_sorted['season'] == current_season].copy()
        
        current_season_df['New In League'] = ~current_season_df['ID'].isin(players_in_previous_season)
        
        df_list.append(current_season_df)
        
    return pd.concat(df_list, ignore_index=True)

def calculate_new_in_team(df):
    """
    Calculates the 'New In Team' feature for each player.

    A player is considered 'New In Team' if they were not in the league
    in the previous season, or if they were in a different team.

    Args:
        df (pd.DataFrame): The DataFrame with player data for all seasons.

    Returns:
        pd.DataFrame: The DataFrame with the 'New In Team' column added.
    """
    df_sorted = df.sort_values('season').reset_index(drop=True)
    seasons = df_sorted['season'].unique()
    
    df_list = []

    # For the first season, 'New In Team' is False for everyone
    first_season_df = df_sorted[df_sorted['season'] == seasons[0]].copy()
    first_season_df['New In Team'] = False
    df_list.append(first_season_df)

    # Iterate from the second season
    for i in range(1, len(seasons)):
        previous_season = seasons[i-1]
        current_season = seasons[i]
        
        previous_season_df = df_sorted[df_sorted['season'] == previous_season]
        current_season_df = df_sorted[df_sorted['season'] == current_season].copy()

        # Create a mapping of player ID to team_code for the previous season
        # Using drop_duplicates to handle cases where a player might have multiple entries per season
        previous_season_teams = previous_season_df[['ID', 'team_code']].drop_duplicates(subset=['ID']).set_index('ID')['team_code']
        
        # Map the previous season's team to the current season's players
        current_season_df['previous_team_code'] = current_season_df['ID'].map(previous_season_teams)
        
        # A player is new in the team if they have no previous team or their team has changed
        current_season_df['New In Team'] = (current_season_df['previous_team_code'].isnull()) | \
                                           (current_season_df['team_code'] != current_season_df['previous_team_code'])
        
        # Drop the helper column
        current_season_df.drop(columns=['previous_team_code'], inplace=True)

        df_list.append(current_season_df)
        
    return pd.concat(df_list, ignore_index=True)

def calculate_additional_features(df):
    """
    Calculates additional features based on past season data.
    - max_minutes_in_position_past_season: For new players in a team, the max minutes
      played by anyone in that position in that team last season.
    - max_minutes_by_signing_past_season: For existing players, the max minutes
      played by a new signing in that team last season.
    - time_in_league: Number of previous seasons the player has been in the league.
    - avg_ppg_position_team_high_minutes: For new players in a team, the average PPG
      of players in the same position and team from the previous season, with >1400 minutes.
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

    # --- New Feature: avg_ppg_position_team_high_minutes ---
    # Pre-calculate average PPG for players with >1400 minutes per team/position for all seasons
    avg_ppg_pos_team = df_sorted[df_sorted['Min'] > 1400].groupby(['season', 'team_code', 'Position'])['PPG'].mean().reset_index()
    avg_ppg_pos_team.rename(columns={'PPG': 'avg_ppg_position_team_high_minutes', 'season': 'previous_season'}, inplace=True)

    # Merge this data into the main dataframe
    df_with_features = pd.merge(
        df_with_features,
        avg_ppg_pos_team,
        how='left',
        left_on=['previous_season', 'team_code', 'Position'],
        right_on=['previous_season', 'team_code', 'Position']
    )
    # Set the value to NaN if the player is not new in the team
    df_with_features['avg_ppg_position_team_high_minutes'] = df_with_features['avg_ppg_position_team_high_minutes'].where(df_with_features['New In Team'], np.nan)

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

def main():
    """
    Main function to load data, calculate features, and explore the result.
    """
    all_data = load_data()
    
    all_data_with_features = calculate_new_in_league(all_data)
    all_data_with_features = calculate_new_in_team(all_data_with_features)
    all_data_with_features = calculate_additional_features(all_data_with_features)
    all_data_with_features = calculate_historical_features(all_data_with_features)
    
    print("Sample of the data with the 'New In League' feature:")
    print(all_data_with_features.head())
    
    print("\nSample of players who are 'New In League':")
    print(all_data_with_features[all_data_with_features['New In League'] == True].head())

    print("\nSample of players who are 'New In Team':")
    print(all_data_with_features[all_data_with_features['New In Team'] == True].head())

    # Add new columns to the print statement for verification
    cols_to_show = [
        'season', 'Player Name', 'Position', 'team_code', 'PPG', 'Min',
        'points_last_season', 'avg_points_last_2_seasons', 'avg_points_last_3_seasons',
        'minutes_last_season', 'avg_minutes_last_2_seasons', 'avg_minutes_last_3_seasons',
        'minutes_last_season_same_team', 'avg_minutes_last_2_seasons_same_team', 'avg_minutes_last_3_seasons_same_team',
        'time_in_league', 'max_minutes_in_position_past_season', 'max_minutes_by_signing_past_season',
        'avg_ppg_position_team_high_minutes'
    ]
    
    #all_data_with_features[all_data_with_features.ID == 446008][cols_to_show]

    print("\n--- Verification of New Columns ---")
    print("\nTime in League (sample):")
    print(all_data_with_features[['Player Name', 'season', 'time_in_league']].tail())

    print("\nMax Minutes in Position (New Players Sample):")
    seasons = sorted(all_data_with_features['season'].unique())
    if len(seasons) > 1:
        new_players_sample = all_data_with_features[
            (all_data_with_features['New In Team'] == True) & (all_data_with_features['season'] > seasons[0])
        ]
        print(new_players_sample[['season', 'Player Name', 'team_code', 'Position', 'max_minutes_in_position_past_season']].head())

    print("\nMax Minutes by Signing (Existing Players Sample):")
    if len(seasons) > 1:
        existing_players_sample = all_data_with_features[
            (all_data_with_features['New In Team'] == False) & (all_data_with_features['season'] > seasons[0])
        ]
        print(existing_players_sample[['season', 'Player Name', 'team_code', 'max_minutes_by_signing_past_season']].head())

    print("\nAverage PPG for New Players in Position (Sample):")
    if len(seasons) > 1:
        new_players_sample = all_data_with_features[
            (all_data_with_features['New In Team'] == True) & (all_data_with_features['season'] > seasons[0])
        ]
        print(new_players_sample[['season', 'Player Name', 'team_code', 'Position', 'avg_ppg_position_team_high_minutes']].head())

    all_data_with_features = all_data_with_features[~all_data_with_features.Position.isna()]
    all_data_with_features
    all_data_with_features.to_csv('fantasy_data_history.csv', index=False)


if __name__ == "__main__":
    main()


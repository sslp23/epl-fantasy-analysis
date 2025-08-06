import pandas as pd
import glob
import os
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import linregress

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

def plot_position_curve_with_slope(df, position):
    """
    Filters data for a specific position, plots a curve of Total Points vs. Player Rank,
    and includes the slope in the title.

    Args:
        df (pd.DataFrame): The DataFrame containing all player data.
        position (str): The position to plot (e.g., 'STR', 'MID', 'DEF').
    """
    df_filtered = df[(df['Min'] > 1200) & (df['Position'] == position)].copy()
    df_sorted = df_filtered.sort_values('Tot Pts', ascending=False).reset_index(drop=True)
    
    slope, intercept, r_value, p_value, std_err = linregress(df_sorted.index, df_sorted['Tot Pts'])
    
    plt.figure(figsize=(12, 8))
    ax = sns.lineplot(x=df_sorted.index, y=df_sorted['Tot Pts'])
    
    title = f'Total Points vs. Player Rank for {position}s (Minutes > 1200)\nSlope: {slope:.2f}'
    ax.set_title(title)
    ax.set_xlabel('Player Rank')
    ax.set_ylabel('Total Points')
    ax.grid(True)
    
    plt.show()
    plt.close()

def plot_position_boxplot(df):
    """
    Creates a boxplot of Total Points for STR, MID, and DEF positions.

    Args:
        df (pd.DataFrame): The DataFrame containing player data.
    """
    df_filtered = df[(df['Min'] > 1200) & (df['Position'].isin(['FWD', 'GK','MID', 'DEF']))].copy()

    plt.figure(figsize=(12, 8))
    sns.boxplot(data=df_filtered, x='Position', y='Tot Pts', hue='Position', palette='viridis')
    
    plt.title('Total Points Distribution by Position (Minutes > 1200)')
    plt.xlabel('Position')
    plt.ylabel('Total Points')
    plt.legend(title='Position')
    plt.grid(True)
    plt.show()
    plt.close()

def plot_average_players_by_season(df):
    """
    Calculates and displays the average number of players per season who meet the criteria (PPG > 4.4 and Min > 1200) for each position as a bar chart.

    Args:
        df (pd.DataFrame): The DataFrame containing all player data.
    """
    df_filtered = df[(df['PPG'] > 4.4) & (df['Min'] > 1200)]
    season_counts = df_filtered.groupby(['season', 'Position']).size().unstack(fill_value=0)
    average_counts = season_counts.mean()

    plt.figure(figsize=(10, 6))
    ax = sns.barplot(x=average_counts.index, y=average_counts.values, palette='viridis', hue=average_counts.index, dodge=False)
    
    for i, v in enumerate(average_counts.values):
        ax.text(i, v + 0.1, f'{v:.2f}', ha='center', va='bottom')

    plt.title('Average Number of Players per Season with PPG > 4.4 and > 1200 Minutes Played')
    plt.xlabel('Position')
    plt.ylabel('Average Number of Players')
    plt.legend([],[], frameon=False)
    plt.show()
    plt.close()

def main():
    """
    Main function to run the analysis.
    """
    all_data = load_data()
    
    positions_to_plot = ['FWD', 'MID', 'DEF']
    
    for position in positions_to_plot:
        plot_position_curve_with_slope(all_data, position)

    plot_position_boxplot(all_data)
    
    all_data[(all_data['Min'] > 1200)].groupby('Position')['PPG'].mean()
    
    plot_average_players_by_season(all_data)

    # Takes:
    # More midfielders in target group 
    # Strikers in general are making more points 



if __name__ == "__main__":
    main()
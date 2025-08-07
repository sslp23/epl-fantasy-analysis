import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def plot_correlation_map(anl_df):
    """
    Plots a correlation map for selected columns of the analysis DataFrame.
    """
    cols_to_correlate = [
        'PPG', 'points_last_season', 'avg_points_last_2_seasons', 
        'avg_points_last_3_seasons', 'minutes_last_season', 
        'avg_minutes_last_2_seasons', 'avg_minutes_last_3_seasons',
        'minutes_last_season_same_team', 'avg_minutes_last_2_seasons_same_team', 
        'avg_minutes_last_3_seasons_same_team'
    ]
    
    correlation_matrix = anl_df[cols_to_correlate].corr()
    
    plt.figure(figsize=(12, 10))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f")
    plt.title('Correlation Map')
    plt.show()

def plot_analysis(anl_df, min_ppg = 4.4, min_minutes = 1200):
    """
    Plots four bar charts from the analysis DataFrame.
    """
    filtered_df = anl_df[(anl_df.Min > min_minutes) & (anl_df.PPG > min_ppg)]

    # Plot 1: Group by 'New In League'
    fig1, ax1 = plt.subplots()
    new_in_league = filtered_df.groupby('New In League').size()
    new_in_league.plot(kind='bar', ax=ax1)
    ax1.set_title('Players on Target Group by New In League')
    for container in ax1.containers:
        ax1.bar_label(container)
    plt.show()

    # Plot 2: Group by 'New In Team'
    fig2, ax2 = plt.subplots()
    new_in_team = filtered_df.groupby('New In Team').size()
    new_in_team.plot(kind='bar', ax=ax2)
    ax2.set_title('Players on Target Group by New In Team')
    for container in ax2.containers:
        ax2.bar_label(container)
    plt.show()

def plot_stats(anl_df, min_ppg=4.4, min_minutes=1200):

    filtered_df = anl_df[(anl_df.Min > min_minutes) & (anl_df.PPG > min_ppg)]
    # Plot 3: Mean of player points stats
    fig3, ax3 = plt.subplots()
    points_cols = ['points_last_season', 'avg_points_last_2_seasons', 'avg_points_last_3_seasons']
    mean_points_stats = filtered_df[points_cols].mean()
    mean_points_stats.plot(kind='bar', ax=ax3)
    ax3.set_title('Mean of Player Points Stats for Target Group')
    for container in ax3.containers:
        ax3.bar_label(container)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show()

    # Plot 4: Mean of player minutes stats
    fig4, ax4 = plt.subplots()
    minutes_cols = ['minutes_last_season', 'avg_minutes_last_2_seasons', 'avg_minutes_last_3_seasons',
                    'minutes_last_season_same_team', 'avg_minutes_last_2_seasons_same_team', 'avg_minutes_last_3_seasons_same_team']
    mean_minutes_stats = filtered_df[minutes_cols].mean()
    mean_minutes_stats.plot(kind='bar', ax=ax4)
    ax4.set_title('Mean of Player Minutes Stats for Target Group')
    for container in ax4.containers:
        ax4.bar_label(container)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show()

def get_ppg_pos(anl_df, pos):
    """
    For each season, finds the PPG of the player at a specific rank (position).

    Args:
        anl_df (pd.DataFrame): The analysis DataFrame.
        pos (int): The rank of the player to select (e.g., 50 for the 50th player).

    Returns:
        pd.Series: A Series with the PPG for the player at the given
                   position for each season.
    """
    # Sort by PPG within each season and get the nth player
    # pos-1 because iloc is 0-indexed
    return anl_df.groupby('season').apply(lambda x: x.sort_values('PPG', ascending=False).iloc[pos-1], include_groups=False).PPG.mean()

def main():
    df = pd.read_csv('fantasy_data_history.csv')

    anl_df = df[(df.season > '2019-20')]

    avg_players_target = anl_df[(anl_df.Min > 1200) & (anl_df.PPG > 4.4)].groupby('season').size().mean()
    print('Players on target group: ', avg_players_target)

    # 24 players on average on this group -> our first 3 round targets
    
    plot_analysis(anl_df)
    plot_correlation_map(anl_df[(anl_df.Min > 1200)])

    ppg_50th = get_ppg_pos(anl_df, 50)
    print("\nPPG of the 50th player each season:", (ppg_50th))

    ppg_50th = get_ppg_pos(anl_df, 70)
    print("\nPPG of the 70th player each season:", (ppg_50th))

    ppg_50th = get_ppg_pos(anl_df, 100)
    print("\nPPG of the 100th player each season:", (ppg_50th))
    
    ppg_50th = get_ppg_pos(anl_df, 125)
    print("\nPPG of the 125th player each season:", (ppg_50th))
    
    ppg_50th = get_ppg_pos(anl_df, 150)
    print("\nPPG of the 150th player each season:", (ppg_50th))

    print('Better than 95% of the players?', anl_df[(anl_df.Min > 1200)].PPG.quantile(0.95))
    
    avg_players_target = anl_df[(anl_df.Min > 1200) & (anl_df.PPG > 5)].groupby('season').size().mean()
    print('Players on target group: ', avg_players_target)
    
    # 13.6 players on average on this group -> targets for first/mid 2nd round

    plot_analysis(anl_df, min_ppg=5)
    


if __name__=='__main__':
    main()

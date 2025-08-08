import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler

def plot_correlation_map(anl_df):
    """
    Plots a correlation map for selected columns of the analysis DataFrame.
    """
    cols_to_correlate = [
        'PPG', 'time_in_league', 'max_minutes_by_signing_past_season', 'points_last_season', 'avg_points_last_2_seasons', 
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
    Plots three bar charts from the analysis DataFrame.
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

    # Plot 3: Average 'New In Team' True/False per season
    fig3, ax3 = plt.subplots()
    new_in_team_per_season = filtered_df.groupby(['season', 'New In Team']).size().unstack(fill_value=0)
    
    average_new_in_team = new_in_team_per_season.mean()

    average_new_in_team.plot(kind='bar', ax=ax3)
    ax3.set_title('Average Players on Target Group per Season by New In Team Status')
    ax3.set_ylabel('Average Count')
    ax3.set_xlabel('New In Team')
    for container in ax3.containers:
        ax3.bar_label(container, fmt='%.1f') # Format to one decimal place for average
    plt.xticks(rotation=0) # Keep labels horizontal
    plt.tight_layout()
    plt.show()

    # Plot 4: Percentage of players with PPG > min_ppg in each 'New In Team' group
    fig4, ax4 = plt.subplots()
    
    # Total players with more than min_minutes, grouped by 'New In Team'
    total_players_by_team_status = anl_df[anl_df.Min > min_minutes].groupby('New In Team').size()
    
    # Players who also meet the min_ppg criteria
    target_players_by_team_status = anl_df[(anl_df.Min > min_minutes) & (anl_df.PPG > min_ppg)].groupby('New In Team').size()
    
    # Calculate the percentage
    percentage_on_target = (target_players_by_team_status / total_players_by_team_status) * 100
    
    percentage_on_target.plot(kind='bar', ax=ax4)
    ax4.set_title(f'% of Players with >{min_minutes} Min who achieved >{min_ppg} PPG')
    ax4.set_ylabel('Percentage (%)')
    ax4.set_xlabel('New In Team')
    for container in ax4.containers:
        ax4.bar_label(container, fmt='%.1f%%')
    plt.xticks(rotation=0)
    plt.tight_layout()
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

def plot_cumulative_ppg_by_time_in_league(target_base):
    """
    Plots the cumulative average of PPG by 'time_in_league'.
    """
    max_time = int(target_base['time_in_league'].max())
    cumulative_avg_ppg = {}

    for i in range(1, max_time + 1):
        cumulative_avg_ppg[f'<={i}'] = target_base[target_base['time_in_league'] <= i]['PPG'].mean()

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(cumulative_avg_ppg.keys(), cumulative_avg_ppg.values())

    ax.bar_label(bars, fmt='%.2f')

    plt.title('Cumulative Average PPG by Time in League')
    plt.xlabel('Time in League (years)')
    plt.ylabel('Average PPG')
    plt.show()

def plot_feature_distribution_by_ppg(target_base, min_ppg=4.4, features = []):
    """
    Plots boxplots of specified features, comparing players above and below a minimum PPG.
    """

    plot_df = target_base.copy()
    plot_df['PPG_Group'] = plot_df['PPG'].apply(lambda x: f'> {min_ppg}' if x > min_ppg else f'<= {min_ppg}')

    # Melt the dataframe to make it suitable for seaborn
    melted_df = plot_df.melt(id_vars='PPG_Group', value_vars=features, var_name='Feature', value_name='Value')

    plt.figure(figsize=(18, 10))
    sns.boxplot(x='Feature', y='Value', hue='PPG_Group', data=melted_df, palette={f'<= {min_ppg}': 'blue', f'> {min_ppg}': 'orange'})
    plt.title('Distribution of Features by PPG Group')
    plt.xlabel('Feature')
    plt.ylabel('Value')
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
    # Players with experience in the team (New In Team = False) are a lot safer bet (even with their sample being smaller)
    # This comes from:
    # 1) Total of 124 players reaching our target (4.4 PPG with more than 1200mins). 105 are Non-New In Team
    # 2) Percentage of Non-New In Team who achieve this target is higher too -> 11.1% against 4.1% (who achieved 1200mins)
    # 3) On average we have 21 players in this group per season -> we can use to find our 1st and 2nd rounders. 

    # Next step: 
    # Analyse which features are good predictors for season's PPG, using Non-New In Team players
    target_base = anl_df[(anl_df.Min > 1200) & (anl_df['New In Team'] == False)]
    plot_correlation_map(target_base)
    # Points in the previous seasons are the more correlated features.
    plot_cumulative_ppg_by_time_in_league(target_base)
    plot_cumulative_ppg_by_time_in_league(target_base[target_base.PPG > 4.4])
    # Second season players have the higher avg PPG between players on the target group who achived more than 4.4
    # But they have the lowest between all players 
    # High risk -> high reward, in general
    features_points = [
        'points_last_season', 'avg_points_last_2_seasons', 
        'avg_points_last_3_seasons']
    
    features_minutes = [ 'minutes_last_season', 
        'avg_minutes_last_2_seasons', 'avg_minutes_last_3_seasons',
        'minutes_last_season_same_team', 'avg_minutes_last_2_seasons_same_team', 
        'avg_minutes_last_3_seasons_same_team'
    ]
    
    plot_feature_distribution_by_ppg(target_base, features=features_points)
    # Past season Points has a clear separation in our target (PPG)
    # Avg in past 2 seasons and past 3 seasons are also a good separator
    # I will use Q1(past_last_season) and Q2 (avg_points_last_2_seasons as an initial threshold.)

    plot_feature_distribution_by_ppg(target_base, features=features_minutes)

    # Past season minutes don't have a clear separation, so I'll use the value of Q1 for avg_minutes_last_2_seasons

    
    target_base.columns

    
    




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
    

if __name__=="__main__": 
    main()



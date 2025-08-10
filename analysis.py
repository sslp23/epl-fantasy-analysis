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

def get_pct_succesfull_new(anl_df, min_ppg = 4.4, min_minutes = 1200, new_in_league = True):
    # This chart looks the % of new in team players who achieved the threshold

    if not new_in_league:
        filtered_df = anl_df[anl_df['New In League'] == False].copy()

        # Plot 4: Percentage of players with PPG > min_ppg in each 'New In Team' group
    fig4, ax4 = plt.subplots()
    
    # Total players with more than min_minutes, grouped by 'New In Team'
    total_players_by_team_status = filtered_df[filtered_df.Min > min_minutes].groupby('New In Team').size()
    
    # Players who also meet the min_ppg criteria
    target_players_by_team_status = filtered_df[(filtered_df.Min > min_minutes) & (filtered_df.PPG > min_ppg)].groupby('New In Team').size()
    
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

def plot_position_distribution_by_ppg(target_base, min_ppg=4):
    """
    Plots a boxplot of PPG for each position, comparing players above and below a minimum PPG.
    For the group with less than min_ppg, it only considers the top 30 players per season per position.
    """
    plot_df = target_base.copy()

    # Separate players into two groups
    above_min_ppg = plot_df[plot_df['PPG'] >= min_ppg]
    below_min_ppg = plot_df[plot_df['PPG'] < min_ppg]

    # For the below_min_ppg group, get the top 30 players per season and position
    top_30_below_min_ppg = below_min_ppg.groupby(['season', 'Position']).apply(lambda x: x.sort_values('PPG', ascending=False).head(30))

    # Combine the filtered 'below' group with the 'above' group
    final_plot_df = pd.concat([above_min_ppg, top_30_below_min_ppg.reset_index(drop=True)])
    
    final_plot_df['PPG_Group'] = final_plot_df['PPG'].apply(lambda x: f'>= {min_ppg}' if x >= min_ppg else f'< {min_ppg}')

    plt.figure(figsize=(12, 8))
    sns.boxplot(x='Position', y='PPG', hue='PPG_Group', data=final_plot_df, palette={f'< {min_ppg}': 'red', f'>= {min_ppg}': 'green'})
    plt.title(f'PPG Distribution by Position for Players with > 1200 Mins')
    plt.xlabel('Position')
    plt.ylabel('Points Per Game (PPG)')
    plt.legend(title='PPG Group')
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
    # I will use Q2(past_last_season) and Q3 (avg_points_last_2_seasons as an initial threshold.)

    plot_feature_distribution_by_ppg(target_base, features=features_minutes)

    # Past season minutes don't have a clear separation, so I'll use the value of Q1 for avg_minutes_last_2_seasons
    filter_1 = target_base[(target_base.PPG > 4.4)].avg_points_last_2_seasons.quantile(0.75)
    filter_2 = target_base[(target_base.PPG > 4.4)].points_last_season.quantile(0.5)
    filter_3 = target_base[(target_base.PPG > 4.4)].avg_minutes_last_2_seasons.quantile(0.25)
    print('Avg Points Last 2 Seasons: ', filter_1)
    print('Avg Points Last Season: ', filter_2)
    print('Avg Minutes Last 2 Seasons: ', filter_3)

    # Next step: round 1 - 3:
    # 1st point: understand the effect of position
    # based on previous analysis is clear that the pool of midfielders is bigger
    # given that, how many rounds we can ignore midfielders? 
    # should we focus our rounds 2-3-4 only on FWDS/DEFS? 
    # Are any MIds worth there? (probably yes, we need to find which)
    # For DEFs and FWDs in this group, follow the same analysis -> which players from these positions are clear giving me more points
    
    # First step to analyse positions:
    # Look at the dropoff of each position
    # I'll do this by plotting the boxplot of avg PPG of each position, only > 1200 mins played, between players with >= 4 PPG and not
    plot_position_distribution_by_ppg(target_base)
    print(target_base[target_base.PPG>4].groupby('Position').size())

    # Based on what we saw:
    # Forwards are clearly scarce and have a higher dropoff on quality -> goal is to get 3 FWDs from 4 first rounds
    # MIDs have a better PPG than DEFs and a simlar dropoff...
    # However, good DEFs are more scarce -> idea is to have strict filters for MIDs.

    plot_feature_distribution_by_ppg(target_base[target_base.Position == 'FWD'], min_ppg=4, features=features_points)
    
    # Filter for FWDs:
    # Split in two types: premium (over Q2 for our 2 features)
    target_base[(target_base.PPG > 4) & (target_base.Position == 'FWD')].avg_points_last_2_seasons.quantile(0.5)
    target_base[(target_base.PPG > 4) & (target_base.Position == 'FWD')].points_last_season.quantile(0.5)

    # common (over Q1)
    target_base[(target_base.PPG > 4) & (target_base.Position == 'FWD')].avg_points_last_2_seasons.quantile(0.25)
    target_base[(target_base.PPG > 4) & (target_base.Position == 'FWD')].points_last_season.quantile(0.25)
    
    # Filter for MIDs:
    plot_feature_distribution_by_ppg(target_base[target_base.Position == 'MID'], min_ppg=4, features=features_points)
    plot_feature_distribution_by_ppg(target_base[target_base.Position == 'MID'], min_ppg=4, features=features_minutes)
    
    # Add minute rule -> important. We have a lot of mids, is crucial to select mids who are playing every game
    # PPG rules -> over Q2
    target_base[(target_base.PPG > 4) & (target_base.Position == 'MID')].avg_points_last_2_seasons.quantile(0.5)
    target_base[(target_base.PPG > 4) & (target_base.Position == 'MID')].points_last_season.quantile(0.5)
    target_base[(target_base.PPG > 4) & (target_base.Position == 'MID')].minutes_last_season.quantile(0.5)

    plot_feature_distribution_by_ppg(target_base[target_base.Position == 'DEF'], min_ppg=4, features=features_points)
    plot_feature_distribution_by_ppg(target_base[target_base.Position == 'DEF'], min_ppg=4, features=features_minutes)

    # minute rule -> not important. Don't differentiate a lot the distributions
    # PPG rules -> over Q5
    target_base[(target_base.PPG > 4) & (target_base.Position == 'DEF')].avg_points_last_2_seasons.quantile(0.5)
    target_base[(target_base.PPG > 4) & (target_base.Position == 'DEF')].points_last_season.quantile(0.5)
    
    # Next steps -> rounds 4/5/6/7
    # GKs need to be analysed
    # We need to open a analysis on New In Team players
    # Keep the analysis split up by positions. 
    # First step, identify our target PPG for this round. I'll use the avg PPG of 70th player per season
    ppg_70th = get_ppg_pos(anl_df, 70)
    print("\nPPG of the 70th player each season:", (ppg_70th))
    
    #Starting by GK
    plot_feature_distribution_by_ppg(target_base[target_base.Position == 'GK'], min_ppg=3.8, features=features_points)
    # points_last_season has small influenceon separating data.
    # I'll use Q3 of avg_points_last_2_seasons, as the first split, since it's above Q3 of the other group.
    target_base[(target_base.PPG > 3.8) & (target_base.Position == 'GK')].avg_points_last_2_seasons.quantile(0.5)

    # For the other positions, first I'll look at the average PPG for New In Team vs Not New in team
    
    # Let's see by defenders:
    get_pct_succesfull_new(anl_df[anl_df.Position == 'DEF'], min_ppg=3.8, new_in_league = False)
    # Only 4% of new in team defenders achieve the threshold. I'll stay away for this group

    # For MIDs
    get_pct_succesfull_new(anl_df[anl_df.Position == 'MID'], min_ppg=3.8, new_in_league = False)
    # 15.2%, so I'll work with very strict thresholds for MIDs New In Team
    
    get_pct_succesfull_new(anl_df[anl_df.Position == 'FWD'], min_ppg=3.8, new_in_league = False)
    # 21.4% also we need to use strict thresholds for FWDs
    
    # Let's look at possible thresholds
    target_new = anl_df[(anl_df.Min > 1200) & (anl_df['New In Team'] == True)]
    # MIDs -  using Q2 of avg last 2 seasons seems good. 
    # MIDs - looking at minutes seems crucial. I'll use Q2 of last season.
    plot_feature_distribution_by_ppg(target_new[target_new.Position == 'MID'], min_ppg=3.8, features=features_points)
    plot_feature_distribution_by_ppg(target_new[target_new.Position == 'MID'], min_ppg=3.8, features=features_minutes)
    target_new[(target_new.PPG > 3.8) & (target_new.Position == 'MID')].avg_points_last_2_seasons.quantile(0.5)
    target_new[(target_new.PPG > 3.8) & (target_new.Position == 'MID')].minutes_last_season.quantile(0.5)

    # MIDs - already in league
    # Q1 is good both for avg_points_last_2_seasons and points_last_season
    # However, since a lot of mids can be on the board, I'll use Q2 for premium (4/5) and the rest will be Q1
    plot_feature_distribution_by_ppg(target_base[target_base.Position == 'MID'], min_ppg=3.8, features=features_points)
    plot_feature_distribution_by_ppg(target_base[target_base.Position == 'MID'], min_ppg=3.8, features=features_minutes)
    target_base[(target_base.PPG > 3.8) & (target_base.Position == 'MID')].avg_points_last_2_seasons.quantile(0.5)
    target_base[(target_base.PPG > 3.8) & (target_base.Position == 'MID')].points_last_season.quantile(0.5)
    target_base[(target_base.PPG > 3.8) & (target_base.Position == 'MID')].minutes_last_season.quantile(0.5)

    target_base[(target_base.PPG > 3.8) & (target_base.Position == 'MID')].avg_points_last_2_seasons.quantile(0.25)
    target_base[(target_base.PPG > 3.8) & (target_base.Position == 'MID')].points_last_season.quantile(0.25)
    target_base[(target_base.PPG > 3.8) & (target_base.Position == 'MID')].minutes_last_season.quantile(0.25)

    #FWDS - already in the league
    # splitting data is almost impossible now, using only FWDS already in the league
    # I'll use the minutes from last season (Q2), and Q2 for avg points last 2 seasons.
    plot_feature_distribution_by_ppg(target_base[target_base.Position == 'FWD'], min_ppg=3.8, features=features_points)
    plot_feature_distribution_by_ppg(target_base[target_base.Position == 'FWD'], min_ppg=3.8, features=features_minutes)
    target_base[(target_base.PPG > 3.8) & (target_base.Position == 'FWD')].avg_minutes_last_2_seasons.quantile(0.5)
    target_base[(target_base.PPG > 3.8) & (target_base.Position == 'FWD')].avg_points_last_2_seasons.quantile(0.5)

    # For new FWDs:
    # Q2 for points last season and avg 2 seasons
    # Q2 for minutes
    plot_feature_distribution_by_ppg(target_new[target_new.Position == 'FWD'], min_ppg=3.8, features=features_points)
    plot_feature_distribution_by_ppg(target_new[target_new.Position == 'FWD'], min_ppg=3.8, features=features_minutes)
    target_new[(target_new.PPG > 3.8) & (target_new.Position == 'FWD')].points_last_season.quantile(0.5)
    target_new[(target_new.PPG > 3.8) & (target_new.Position == 'FWD')].avg_points_last_2_seasons.quantile(0.5)
    target_new[(target_new.PPG > 3.8) & (target_new.Position == 'FWD')].minutes_last_season.quantile(0.5)

    
    # DEFs
    # Minutes aren't too important, so I'll use 1400 as threshold (lower bound of the both groups)
    # I'll use Q1 of both groups as threshold for points
    plot_feature_distribution_by_ppg(target_base[target_base.Position == 'DEF'], min_ppg=3.8, features=features_points)
    plot_feature_distribution_by_ppg(target_base[target_base.Position == 'DEF'], min_ppg=3.8, features=features_minutes)
    target_base[(target_base.PPG > 3.8) & (target_base.Position == 'DEF')].points_last_season.quantile(0.25)
    target_base[(target_base.PPG > 3.8) & (target_base.Position == 'DEF')].avg_points_last_2_seasons.quantile(0.25)

    # Now GKs, MIDs and DEFs have some options, so I'll work with lowering thresholds
    # FWDs -> trying to find good PPG in lower mins played
    ppg_100th = get_ppg_pos(anl_df, 100)
    print("\nPPG of the 100th player each season:", (ppg_100th))
    # Our target is to find players with >3.5 PPG. Let's see what makes difference to achieve this on DEFs
    
    get_pct_succesfull_new(anl_df[anl_df.Position == 'DEF'], min_ppg=3.5, new_in_league = False)
    # Since 9% of new in team players are beating this minimum of 3.5 PPG, I'll look at new in league
    plot_feature_distribution_by_ppg(target_new[target_new.Position == 'DEF'], min_ppg=3.5, features=features_points)
    plot_feature_distribution_by_ppg(target_new[target_new.Position == 'DEF'], min_ppg=3.5, features=features_minutes)
    
    # I'll use Q1 in points last season and Q2 in minutes
    target_new[(target_new.PPG > 3.5) & (target_new.Position == 'DEF')].avg_minutes_last_2_seasons.quantile(0.5)
    target_new[(target_new.PPG > 3.5) & (target_new.Position == 'DEF')].points_last_season.quantile(0.25)

    # Same analysis for players that aren't new in team
    plot_feature_distribution_by_ppg(target_base[target_base.Position == 'DEF'], min_ppg=3.5, features=features_points)
    plot_feature_distribution_by_ppg(target_base[target_base.Position == 'DEF'], min_ppg=3.5, features=features_minutes)
    
    # I'll use Q1 in points last season. Minutes aren't a huge differentiator
    target_base[(target_base.PPG > 3.5) & (target_base.Position == 'DEF')].avg_minutes_last_2_seasons.quantile(0.5)
    target_base[(target_base.PPG > 3.5) & (target_base.Position == 'DEF')].points_last_season.quantile(0.25)

    # Let's take a look at mifielders
    plot_feature_distribution_by_ppg(target_base[target_base.Position == 'MID'], min_ppg=3.5, features=features_points)
    plot_feature_distribution_by_ppg(target_base[target_base.Position == 'MID'], min_ppg=3.5, features=features_minutes)

    # Since I'm using a high threshold for minutes for MIDs, now I'll stick with the Q1 for minutes_last_season, that's lower
    # Also I'll use Q1 of points_last_season. To get more outsiders (focus of 7+ picks)
    target_base[(target_base.PPG > 3.5) & (target_base.Position == 'MID')].minutes_last_season.quantile(0.25)
    target_base[(target_base.PPG > 3.5) & (target_base.Position == 'MID')].points_last_season.quantile(0.25)

    # For FWDs -> most starters are already out. Time to look what players with less than 1500 mins and more than 500 mmins IN THE PREVIOUS SEASON can give
    lower_mins = anl_df[(anl_df.minutes_last_season < 1500) & (anl_df.minutes_last_season > 500)]
    # Our goal is to find FWDs with few minutes in past season and more minutes in his next season (and points)
    plot_feature_distribution_by_ppg(lower_mins[lower_mins.Position == 'FWD'], min_ppg=3.5, features=features_points)
    plot_feature_distribution_by_ppg(lower_mins[lower_mins.Position == 'FWD'], min_ppg=3.5, features=features_minutes)

    # The distributions are slightly similar...
    # Minutes past season (Q3) seems to have some predictability. Also points_last_season can give some insights
    lower_mins[(lower_mins.PPG > 3.5) & (lower_mins.Position == 'MID')].minutes_last_season.quantile(0.75)
    lower_mins[(lower_mins.PPG > 3.5) & (lower_mins.Position == 'MID')].points_last_season.quantile(0.5)

    # GKs...
    # A lot still available, so let's do the traditional analysis.
    plot_feature_distribution_by_ppg(target_base[target_base.Position == 'GK'], min_ppg=3.5, features=features_points)
    plot_feature_distribution_by_ppg(target_base[target_base.Position == 'GK'], min_ppg=3.5, features=features_minutes)

    # There is no clear difference there. 
    # Let's use 2500 mins a mins threshold
    # And Q1 points last season
    target_base[(target_base.PPG > 3.5) & (target_base.Position == 'GK')].points_last_season.quantile(0.25)

    # Tier 5 -> last tier before selecting only based on initial schedule
    ppg_125th = get_ppg_pos(anl_df, 125)
    print("\nPPG of the 125th player each season:", (ppg_125th))
    # Idea is to get players who performed bad last season, but have some indicators that can get a better performance
    lower_mins = anl_df[(anl_df.points_last_season < 3.5) & (anl_df.minutes_last_season > 800)]
    
    # Our goal is to find FWDs with few minutes in past season and more minutes in his next season (and points)
    plot_feature_distribution_by_ppg(lower_mins[lower_mins.Position == 'DEF'], min_ppg=3.3, features=features_points)
    plot_feature_distribution_by_ppg(lower_mins[lower_mins.Position == 'DEF'], min_ppg=3.3, features=features_minutes)
    
    # We have higher Q3 for avg last 2 seasons minutes and a higher Q2 for avg points last season
    # It can indicates to keep an eye on players with some experience
    lower_mins[(lower_mins.PPG > 3.3) & (lower_mins.Position == 'DEF')].avg_minutes_last_2_seasons.quantile(0.75)
    lower_mins[(lower_mins.PPG > 3.3) & (lower_mins.Position == 'DEF')].avg_points_last_2_seasons.quantile(0.5)

    # FOR MIDs
    # First idea: low threshold, focused only on past performance for players with more than one season
    # So, using avg_points_last_2_seasons or even avg_points_last_3_seasons
    lower_mins = anl_df[(anl_df.points_last_season < 3.5) & (anl_df.minutes_last_season > 800) & (anl_df.time_in_league > 2)]
    plot_feature_distribution_by_ppg(lower_mins[lower_mins.Position == 'MID'], min_ppg=3.3, features=features_points)
    plot_feature_distribution_by_ppg(lower_mins[lower_mins.Position == 'MID'], min_ppg=3.3, features=features_minutes)

    lower_mins[(lower_mins.PPG > 3.3) & (lower_mins.Position == 'MID')].avg_points_last_2_seasons.quantile(0.5)
    # Idea is to be use a wide threshold, but focused on previous performance for players with more than one season
    # For players with time_in_league <=2, o a different analysis based on last season
    lower_mins = anl_df[(anl_df.points_last_season < 3.5) & (anl_df.minutes_last_season > 800) & (anl_df.time_in_league <= 2)]
    plot_feature_distribution_by_ppg(lower_mins[lower_mins.Position == 'MID'], min_ppg=3.3, features=features_points)
    plot_feature_distribution_by_ppg(lower_mins[lower_mins.Position == 'MID'], min_ppg=3.3, features=features_minutes)

    lower_mins[(lower_mins.PPG > 3.3) & (lower_mins.Position == 'MID')].points_last_season.quantile(0.5)

    # FOR FWDs
    # Last group, I'll split the analysis
    # First looking at FWDs with not too much points, but a lot of minutes
    plot_feature_distribution_by_ppg(target_base[target_base.Position == 'GK'], min_ppg=3.3, features=features_points)
    plot_feature_distribution_by_ppg(target_base[target_base.Position == 'GK'], min_ppg=3.3, features=features_minutes)

    target_base[(target_base.PPG > 3.3) & (target_base.Position == 'GK')].avg_points_last_2_seasons.quantile(0.25)
    lower_mins[(lower_mins.PPG > 3.3) & (lower_mins.Position == 'FWD')].points_last_season.quantile(0.75)








    




    ppg_50th = get_ppg_pos(anl_df, 50)
    print("\nPPG of the 50th player each season:", (ppg_50th))

    

    ppg_50th = get_ppg_pos(anl_df, 100)
    print("\nPPG of the 100th player each season:", (ppg_50th))
    
    
    
    ppg_50th = get_ppg_pos(anl_df, 150)
    print("\nPPG of the 150th player each season:", (ppg_50th))

    print('Better than 95% of the players?', anl_df[(anl_df.Min > 1200)].PPG.quantile(0.95))
    
    avg_players_target = anl_df[(anl_df.Min > 1200) & (anl_df.PPG > 5)].groupby('season').size().mean()
    print('Players on target group: ', avg_players_target)
    
    # 13.6 players on average on this group -> targets for first/mid 2nd round

    plot_analysis(anl_df, min_ppg=5)
    

if __name__=="__main__": 
    main()



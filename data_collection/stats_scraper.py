import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
from selenium import webdriver

"""
Loop through the dates: Modify the url at each loops so each loop has the url for the next day
Loop through all the games in one day and retrieve the necessary stats
"""


def get_date_links(year):
    """
    Takes in a year
    Returns a list of links corresponding to all the scores for one day

    ex: returns list filled with urls like https://www.espn.com/mlb/scoreboard/_/date/20180329
    """
    url = "https://www.espn.com/mlb/scoreboard/_/date/"
    dates = pd.read_excel(f'yearly_odds\mlb odds {year}.xlsx')['Date']
    dates = dates.astype('string').apply(lambda x: '0' + x if len(x) == 3 else x)
    dates = dates.unique()

    date_links = [f"{url}{year}{date}" for date in dates]

    return date_links


def get_box_score_links(url, path):
    """
    Takes in a url for all the scores for one day and path to web driver
    Returns a list of the links to the box scores for one day


    ex: returns list filled with urls like https://www.espn.com/mlb/boxscore/_/gameId/380329121
    """
    driver = webdriver.Chrome(path)
    driver.get(url)
    page = bs(driver.page_source, 'html.parser')
    driver.quit()

    scores = page.find_all('a', {'name': '&lpos=mlb:scoreboard:boxscore'})
    links = [f"https://www.espn.com{i['href']}" for i in scores]
    return links


def one_game_stats(url, date):
    """
    Takes in the box score url and date of an espn box score and returns the batting average of the starting rotation
    and the
    era of the starting rotation
    in a data frame of a single row
    """

    html = requests.get(url)
    page = bs(html.text, 'html.parser')

    teams = [i.text for i in page.find_all('span', {'class': 'linescore__abbrev'})]

    gamescore = page.find_all('table', {'data-type':'batting'})
    roster_away = gamescore[0].find_all('tbody')
    lineup_away = [len(roster_away[i]['class'])==1 for i in range(len(roster_away))]

    roster_home = gamescore[1].find_all('tbody')
    lineup_home = [len(roster_home[i]['class'])==1 for i in range(len(roster_home))]

    dfs = pd.read_html(html.text)
    dfs = [df for df in dfs if df.columns[0] in ['Hitters', 'Pitchers']]

    away_hit = dfs[0][lineup_away][:9]['AVG'].to_list()
    away_pitch = [dfs[1].loc[0]['ERA']]
    home_hit = dfs[2][lineup_home][:9]['AVG'].to_list()
    home_pitch = [dfs[3].loc[0]['ERA']]

    stats = [date] + home_hit + home_pitch + away_hit + away_pitch + teams
    stat_labels = ['Date'] + [f'Home AVG {i}' for i in range(1, 10)] + ['Home ERA'] + [f'Visit AVG {i}' for i in
                                                                                       range(1, 10)] + ['Visit ERA'] + [
                      'Visit Team', 'Home Team']

    temp_df = pd.DataFrame.from_dict(dict(zip(stat_labels, stats)), orient='index').T

    return temp_df

def get_yearly_stats(year, path):
    """
    Takes in a year and returns a dataframe of all the game stats for one year
    """
    date_links = get_date_links(year)
    stats_df = pd.DataFrame(
        columns=[f'Home AVG {i}' for i in range(1, 10)] + ['Home ERA'] + [f'Visit AVG {i}' for i in range(1, 10)] + [
            'Visit ERA'])

    i = 1
    for date_link in date_links:
        box_score_links = get_box_score_links(date_link, path)
        print(i)
        i += 1

        for box_score_link in box_score_links:
            try:
                temp_df = one_game_stats(box_score_link, date_link[-4:])
            except:
                continue
            stats_df = stats_df.append(temp_df)

    return stats_df


if __name__ == "__main__":

    PATH = "D:\Github\over_under\data_collection\\chromedriver.exe"

    # year = 2018
    # stats_2018 = get_yearly_stats(year, PATH)
    # stats_2018.to_csv(f'yearly_stats\\{year}_stats.csv', index=False)

    for year in range(2010, 2018):
        print(year)
        stats_2018 = get_yearly_stats(year, PATH)
        stats_2018.to_csv(f'yearly_stats\\{year}_stats.csv', index=False)

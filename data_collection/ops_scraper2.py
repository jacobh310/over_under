import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from datetime import datetime
import numpy as np

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
    s = Service(path)
    driver = webdriver.Chrome(service=s)
    driver.get(url)
    page = bs(driver.page_source, 'html.parser')
    driver.quit()

    scores = page.find_all('a', {'class': 'AnchorLink Button Button--sm Button--anchorLink Button--alt mb4 w-100 mr2'})
    links = [f"https://www.espn.com{i['href']}" for i in scores]
    links = [link for link in links if 'boxscore' in link]

    return links


def get_gamelog_urls(url,year):
    """
    Takes in the box score url, date, and year and returns a list of urls of the starting lineups including starting pitchers that links the the players gamelog
    """

    html = requests.get(url)
    page = bs(html.text, 'html.parser')

    teams = [i.text for i in page.find_all('span', {'class': 'linescore__abbrev'})]

    # Starting pitching ids
    pitchers = page.find_all('table', {'data-type':'pitching'})
    p_roster_away = pitchers[0].find_all('tbody')
    p_roster_home = pitchers[1].find_all('tbody')

    p_id_away = [p_roster_away[i]['data-athlete-id'] for i in range(len(p_roster_away[:-1])) if len(p_roster_away[i]['class'])==1][0]
    p_id_home = [p_roster_home[i]['data-athlete-id'] for i in range(len(p_roster_home[:-1])) if len(p_roster_home[i]['class'])==1][0]

    # Starting line up ids
    gamescore = page.find_all('table', {'data-type':'batting'})
    roster_away = gamescore[0].find_all('tbody')
    roster_home = gamescore[1].find_all('tbody')

    # Combine startin lineup ids
    ids_away = [roster_away[i]['data-athlete-id'] for i in range(len(roster_away[:-1])) if len(roster_away[i]['class'])==1]
    ids_home = [roster_home[i]['data-athlete-id'] for i in range(len(roster_home[:-1])) if len(roster_home[i]['class'])==1]

    pitch_links = [f'https://www.espn.com/mlb/player/gamelog/_/id/{id}/year/{year}/category/pitching' for id in [p_id_away] + [p_id_home]]

    all_bats = ids_away + ids_home
    bat_links = [f'https://www.espn.com/mlb/player/gamelog/_/id/{id}/year/{year}/category/batting' for id in all_bats]

    bat_links.insert(9,pitch_links[0])
    bat_links.insert(19,pitch_links[1])

    return bat_links, teams


def get_game_stats(links, date, year, teams):
    """
    Takes in list of player gamelog links, date(day+month) and year and returns the ops for starting lineup and eras for starting pitchers
    """
    stats = []
    for i in range(len(links)):
        try:
            dfs = pd.read_html(links[i])
        except:
            stat = np.nan
            stats.append(stat)
            continue

        whole = pd.DataFrame()
        for df in dfs:
            if 'Date' in df.columns and df.tail(1)['Date'].values[0] != 'Postseason':
                df = df.drop_duplicates(subset='Date')[:-1]
                df = df[~(df['Date'].str.contains('iously '))]
                df['Date'] = df['Date'].str[4:].str.replace("/", '') + str(year)
                whole = pd.concat([whole, df], axis=0)

        whole['Date'] = whole['Date'].apply(lambda x: datetime.strptime(x, '%m%d%Y').date())
        whole = whole.reset_index().drop(columns='index')

        dt = datetime.strptime(f'{date}{year}', '%m%d%Y').date()
        index = whole[whole['Date'] == dt].index[0]
        if i in [9, 19]:
            try:
                stat = whole.loc[index + 1]['ERA']
            except:
                stat = np.nan
        else:
            try:
                stat = whole.loc[index + 1]['OPS']
            except:
                stat = np.nan
        stats.append(stat)
    stats = [str(date)] + stats + teams
    stats_labels = ['Date'] + [f'Visit OPS {i}' for i in range(1, 10)] + ['Visit Pitcher ERA'] + [f'Home OPS {i}' for i
                                                                                                  in range(1, 10)] + [
                       'Home Pitcher ERA'] + ['Visit Team', 'Home Team']

    df = pd.DataFrame.from_dict(dict(zip(stats_labels, stats)), orient='index').T

    return df


def get_yearly_stats(year, path):
    """
    Takes in a year and returns a dataframe of all the game stats for one year
    """
    date_links = get_date_links(year)
    stats_df = pd.DataFrame(
        columns=['Date'] + [f'Home OPS {i}' for i in range(1, 10)] + ['Home Pitcher ERA'] + [f'Visit OPS {i}' for i in range(1, 10)] + ['Visit Pitcher ERA']+ ['Visit Team', 'Home Team'])

    i = 1
    for date_link in date_links[15:]:
        box_score_links = get_box_score_links(date_link, path)
        print(i)
        i += 1

        for box_score_link in box_score_links:
            try:

                links, teams = get_gamelog_urls(box_score_link, year)
                temp_df = get_game_stats(links, date_link[-4:], year, teams)
            except:
                continue
            if temp_df.shape[1] == 23:
                stats_df = pd.concat([stats_df, temp_df], axis=0)

        stats_df = stats_df.drop_duplicates()

    return stats_df


if __name__ == "__main__":

    PATH = "C:\Personal\Github\over_under\data_collection\\chromedriver.exe"

    # year = 2018
    # stats_2018 = get_yearly_stats(year, PATH)
    # stats_2018.to_csv(f'yearly_stats\\{year}_stats.csv', index=False)

    for year in range(2019, 2023):
        print(year)
        stats = get_yearly_stats(year, PATH)
        stats.to_csv(f'yearly_ops\\ops_{year}_stats.csv', index=False)

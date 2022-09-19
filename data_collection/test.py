import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from ops_scraper2 import *
import time




PATH = "C:\Personal\Github\over_under\data_collection\\chromedriver.exe"
year = 2015


date_links = get_date_links(year)
stats_df = pd.DataFrame(
    columns=['Date'] + [f'Home OPS {i}' for i in range(1, 10)] + ['Home Pitcher ERA'] + [
        f'Visit OPS {i}' for i in range(1, 10)] + ['Visit Pitcher ERA']+ ['Visit Team', 'Home Team'])

# box_score_links = get_box_score_links(date_links[15], PATH)
# links, teams = get_gamelog_urls(box_score_links[0], year)
# temp_df = get_game_stats(links, date_links[15][-4:], year, teams)
#
# print(links)
# print(teams)
# print(box_score_links)
print(date_links[15])

start= time.time()
i = 1
for date_link in date_links[15:18]:
    box_score_links = get_box_score_links(date_link, PATH)
    print(i)
    i += 1

    for box_score_link in box_score_links:
        print(box_score_link)
        links, teams = get_gamelog_urls(box_score_link, year)
        temp_df = get_game_stats(links, date_link[-4:], year, teams)

        stats_df = pd.concat([stats_df, temp_df], axis=0)

    stats_df = stats_df.drop_duplicates()

end = time.time()
print(stats_df)
print(end-start)
#


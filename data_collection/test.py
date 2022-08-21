import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service


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

    scores = page.find_all('a', {'name': '&lpos=mlb:scoreboard:boxscore'})
    links = [f"https://www.espn.com{i['href']}" for i in scores]
    return links


PATH = "C:\Personal\Github\over_under\data_collection\\chromedriver.exe"
url = 'https://www.espn.com/mlb/boxscore/_/gameId/380329121'

links_ = get_box_score_links(url, PATH)

print(links_)

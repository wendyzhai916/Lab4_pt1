# run main.py and the processed scraped data will be stored in database
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import time


def scrape():
    '''
    Jade's part
    output: a dataframe. Each row represent a post, and columns are features extracted from that post
    '''
    # initialize a webdriver to control chrome
    driver = webdriver.Firefox()
    # the url of the target page to scrape
    url = "https://www.reddit.com/r/tech"
    # connect to the target URL in selenium
    driver.get(url)

    # scroll down
    i = 1
    scroll_pause_time = 1
    # retrieve the list of post HTML elements
    posts = []
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        i += 1
        time.sleep(scroll_pause_time)
        if i == 5:
            break
            
    # bs4     
    soup = BeautifulSoup(driver.page_source, "html.parser")
    # find all the posts
    articles = soup.find_all(class_="w-full m-0")
    # for every post, get info
    posts = []
    for article in articles:
        post = {}
        post['title'] = article['aria-label']
        post['author'] = article.find('shreddit-post')['author']
        post['timestamp'] = article.find('shreddit-post')['created-timestamp']
        # img src: have troubles with it
        # resource link?
        posts.append(post)

    df_posts = pd.DataFrame.from_dict(posts,orient='columns')
    driver.quit()

    return df_posts


def process(raw_df):
    '''
    Wendy & Lorenzo's part
    input: the dataframe returned by the scrape() function
    output: the processed dataframe that is about to be stored in db
    '''
    return


def write_to_db(processed_df):
    '''
    input: the dataframe returned by the process() function
    '''
    return


if __name__ == "__main__":
    raw_df = scrape()
    processed_df = process(raw_df)
    write_to_db(processed_df)

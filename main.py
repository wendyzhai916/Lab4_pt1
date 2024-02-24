# run main.py and the processed scraped data will be stored in database
import time
import sys
import keyboard
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver

import nltk
nltk.download('stopwords')
nltk.download('punkt')
from rake_nltk import Rake
from msticpy.data import data_obfus

from sqlalchemy import create_engine

import cluster


def scrape(post_num):
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
    # number of times should the driver perform the scrolling down actions
    scroll_cnt = max(1, round(post_num / 10)) 
    # retrieve the list of post HTML elements
    posts = []
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        i += 1
        time.sleep(scroll_pause_time)
        if i > scroll_cnt:
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
        #post['image url'] = article.find('img', class_='ImageBox-image')['src']
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
    processed_df = raw_df.drop_duplicates()
    #processed_df['timestamp'] = pd.to_datetime(processed_df['timestamp'], unit='s')
    #processed_df['domain'] = processed_df['title'].str.extract(r'\((.*?)\)')
    #processed_df.drop(columns=['title'], inplace=True)
    #processed_df.rename(columns={'author': 'post_author', 'timestamp': 'post_timestamp'}, inplace=True)

    keyword_list = []
    for item in processed_df['title']:
        rake = Rake() # create rake object
        rake.extract_keywords_from_text(item) 
        score_phrase_pair = rake.get_ranked_phrases_with_scores() # return key phrases and its scores 
        # limit phrases with score that is 4 and up
        phrase_with_scores_five_and_up = [(score, phrase) for score, phrase in score_phrase_pair if score>=4]
        # limit topic phrases to 5
        phrase_with_scores_five_and_up = phrase_with_scores_five_and_up[:5]
        keyword_list.append(phrase_with_scores_five_and_up)

    processed_df['keywords'] = keyword_list	
    # turn the list into string so that it can be stored in db
    processed_df['keywords'] = processed_df['keywords'].apply(lambda x: ','.join(map(str, x)))
    masked_user = []
    for username in processed_df['author']:
        masked_user.append(data_obfus.hash_account(username))

    processed_df['masked user'] = masked_user

    return processed_df


def write_to_db(df):
    try:
        df.to_sql(table_name, con=engine, if_exists='append', index=False)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        engine.dispose()
    print("Stored Successfully")


def on_key_event(event):
    if event.name == 'quit':
        print("Exiting thr program...")
        keyboard.unhook_all()
        quit()


if __name__ == "__main__":
    # Invalid sys input
    if len(sys.argv) != 2:
        print("Usage: python3 main.py interval_in_minutes")
        sys.exiit(1)
    try: 
        interval = int(sys.argv[1])
        if interval <= 0:
            raise ValueError
    except ValueError:
        print("Please input a positive integer as interval_in_minutes")

    # keyboard monitor
    #keyboard.on_press(on_key_event)

    # get the number of posts to be scraped for every interval
    print("Please enter the approximate number of posts you wish to scrape for every interval(didn't set 5000 in default bc it will take a long time)")
    post_num = int(input("The number: "))

    # db configuration
    print("PLease enter the configuration information about your database, separated by commas: host, user, password, database")
    print("MAKE SURE you already have the DATABASE in your own machine")
    config_list = input("Input Example, localhost, root, yout_password, your_db: ")
    host = config_list.split(',')[0].strip()
    user = config_list.split(',')[1].strip()
    password = config_list.split(',')[2].strip()
    database = config_list.split(',')[3].strip()
    # connect to db:
    db_config = {
        'host': host,
        'user' : user,
        'password' : password,
        'database' : database
    }
    engine = create_engine('mysql+mysqlconnector://{user}:{password}@{host}/{database}'.format(**db_config))
    
    while True:
        # get the final processed df
        df_raw = scrape(post_num)
        print("Scraped Successfully")
        print("Start Data Processing...")
        df_processed = process(df_raw)
        print("Processed Successfully")
        print("The processed scraped data for the current interval is as belows: ")
        print(df_processed)

        # clustering
        vector_df = cluster.document_vector(df_processed)
        clustered_df = cluster.cluster_and_identify_keywords(vector_df)
        # The visulization of the clusters are as below:
        cluster.draw_cluster(clustered_df)

        # update the db
        print("Writing to the database...")
        table_name = input("Please enter the table name you want for this data in your database: ")
        write_to_db(df_processed)
        print("The database has been updated successfully!")
        print("\n")

        # waiting fot the next round until input "quit"
        print(f"Waiting for the next round, the interval is {interval} minutues")
        flag = input("If you don't want to continue, input 'quit' to exit (or enter anything else if don't want to exit): ")
        if flag == "quit":
            print("Exiting the program...")
            break
        try:
            print("Waiting...")
            time.sleep(interval*60)
        except KeyboardInterrupt:
            print("Interrupted by user")
            break
        

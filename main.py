# run main.py and the processed scraped data will be stored in database
import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import nltk
nltk.download('stopwords')
nltk.download('punkt')
from rake_nltk import Rake


options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
# URL = "https://www.cnbc.com/world/?region=world"
# driver.get(URL)
# time.sleep(5)
# html = driver.page_source
# soup = BeautifulSoup(html, "html.parser")
# with open("../data/raw_data/web_data.html", "w") as file:
#  file.write(soup.prettify())
# driver.close()


def scrape():
    '''
    Jade's part
    output: a dataframe. Each row represent a post, and columns are features extracted from that post
    '''
    # initialize a webdriver to control chrome
    # driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver = webdriver.Firefox()
    # the url of the target page to scrape
    url = "https://www.reddit.com/r/tech"
    # connect to the target URL in selenium
    driver.get(url)
    time.sleep(5)
    html = driver.page_source

    # scroll down
    i = 1
    scroll_pause_time = 1
    # retrieve the list of post HTML elements
    posts = []
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        i += 1
        time.sleep(scroll_pause_time)
        if i == 10:
            break
            
    # bs4     
    soup = BeautifulSoup(html, "html.parser")
    # find all the posts
    articles = soup.find_all(class_="w-full m-0")
    # for every post, get info
    posts = []
    for article in articles:
        post = {}
        post['title'] = article['aria-label']
        post['author'] = article.find('shreddit-post')['author']
        post['timestamp'] = article.find('shreddit-post')['created-timestamp']
        # For every post, get the image URL if available
        post['image url'] = article.find('img', class_='ImageBox-image')['src']
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
    processed_df = raw_df.drop_duplicates()
    processed_df['timestamp'] = pd.to_datetime(processed_df['timestamp'], unit='s')
    processed_df['domain'] = processed_df['title'].str.extract(r'\((.*?)\)')
    processed_df.drop(columns=['title'], inplace=True)
    processed_df.rename(columns={'author': 'post_author', 'timestamp': 'post_timestamp'}, inplace=True)

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
	
    return processed_df

def write_to_db(processed_df):
    '''
    input: the dataframe returned by the process() function
    '''
    return


if __name__ == "__main__":
    raw_df = scrape()
    processed_df = process(raw_df)
    write_to_db(processed_df)

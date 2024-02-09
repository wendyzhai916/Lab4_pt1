# run main.py and the processed scraped data will be stored in database

def scrape():
    '''
    Jade's part
    output: a dataframe. Each row represent a post, and columns are features extracted from that post
    '''
    return


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

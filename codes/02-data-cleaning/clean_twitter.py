import pandas as pd
import os
import fnmatch
import json
import re
from tqdm import tqdm

inc_ids_twtr = pd.read_csv('./../../data/01-modified-data/SSDB/incident_twitter.csv')['Incident_ID']

tweets_raw_rel_path = './../../../large_data/00-raw-data/Twitter/'
output_rel_path = './../../../large_data/02-clean-data/Twitter/'

# Initialize list to load with dataframes for all incident IDs
all_tweets_list = []

for inc_id in tqdm(inc_ids_twtr):    
    # Initialize list to load with dataframes of tweets for the given incident ID
    inc_tweets_list = []

    for filename in os.listdir(tweets_raw_rel_path):
        if fnmatch.fnmatch(filename, inc_id + '*'):
            # Read in json file
            data = json.load(open(tweets_raw_rel_path + filename))

            # Convert data section of json file to pandas df (assuming there is a data section)
            try:
                df_raw = pd.DataFrame(data['data'])
            except KeyError:
                continue

            # Filter out non-English tweets, reset index
            df_raw_en = df_raw[df_raw['lang'] == 'en'].reset_index()

            # Take only the text (tweet) column and copy it as a new df
            df_tweets = df_raw_en[['text']].copy()

            # Remove '\t', '\r' and '\n' whitespaces with single space
            df_tweets['text'] = [tweet.replace('\t', ' ').replace('\n', ' ').replace('\r', ' ') for tweet in df_tweets['text']]

            # Add incident ID column to df_tweets
            df_tweets['Incident_ID'] = inc_id

            # Cycle through each tweet and save the hashtags
            hashtags = []
            for twt in df_tweets['text']:
                hashtags.append(re.findall(r"#(\w+)", twt))

            # Convert all hashtags to lowercase
            hashtags_lwr = [[ht.lower() for ht in ht_set] for ht_set in hashtags]

            # Join hashtag data onto tweets dataframe
            df_tweets = df_tweets.join(pd.DataFrame(hashtags_lwr).add_prefix('ht_'))

            # Append dataframe to inc_tweets_list
            inc_tweets_list.append(df_tweets)

            # Append dataframe to all_tweets_list
            all_tweets_list.append(df_tweets)

    # Concatenate all dataframes in the list into one dataframe (assuming there are dataframes to concatenate)
    try:
        df_tweets_clean = pd.concat(inc_tweets_list, ignore_index=True)
    except ValueError:
        continue

    # Export clean dataframe
    df_tweets_clean.to_csv(output_rel_path + inc_id + '.tsv', sep='\t', index=False)

print("Combining all tweets into one dataset...")
# Concatenate all dataframes from every incident into one dataframe
df_tweets_all = pd.concat(all_tweets_list, ignore_index=True)

print("Removing duplicates...")
df_tweets_all = df_tweets_all.drop_duplicates(subset=['text'], keep='last')

print("Saving dataset of all tweets...")
# Export dataframe of all tweets
df_tweets_all.to_csv(output_rel_path + 'all_tweets.tsv', sep='\t', index=False)

print("Complete.")
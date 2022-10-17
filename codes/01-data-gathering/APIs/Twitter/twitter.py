import json 
import pandas as pd
import requests
import time
from tqdm import tqdm

# Read API key credentials
api = pd.read_json('~/Coding/APIs/twitter_keys.json')['DSAN_501-project']

# Save credentials
consumer_key=api.loc["key"]
consumer_secret=api.loc["key_secret"]
access_token=api.loc["access_token"]
access_token_secret=api.loc["access_token_secret"]
bearer_token=api.loc["bearer_token"]


# PREPARE AND ORGANIZE DATA
# Read in dataset
incidents = pd.read_csv('../../../../data/02-clean-data/SSDB/incident.csv')
incidents['Date'] = pd.to_datetime(incidents['Date'])

# Filter out incidents that occurred before 2006-03-21 (day of first ever tweet)
incidents_twitter = incidents.copy()[incidents['Date'] > pd.to_datetime('2006-03-21 15:50:00')]

# Add new data column marking one week after the incident
incidents_twitter['Date_Week_Later'] = incidents_twitter['Date'] + pd.Timedelta(days=7)

# Convert date columns to YYYY-MM-DDTHH:mm:ssZ (ISO 8601/RFC 3339) for API requests
incidents_twitter['Query_Date'] = incidents_twitter['Date'].dt.strftime('%Y-%m-%d') + "T00:00:00Z"
incidents_twitter['Query_Date_Week_Later'] = incidents_twitter['Date_Week_Later'].dt.strftime('%Y-%m-%d') + "T00:00:00Z"

# Save incidents_twitter as csv
incidents_twitter.to_csv('./../../../../data/01-modified-data/SSDB/incident_twitter.csv', index=False)

# Replace & with and in school names
new_schools = [str(school).replace('&', 'and') for school in incidents_twitter['School']]

# Construct get request parameters, save IDs to list
ids = incidents_twitter['Incident_ID']
queries = "-is:retweet ((school (shooting OR shootings)) OR (" + incidents_twitter['City'] + " (shooting OR shootings)) OR (\"" + new_schools + "\"))"
start_times = incidents_twitter['Query_Date']
end_times = incidents_twitter['Query_Date_Week_Later']


# EXCEPTIONS
# Remove school name from 110th incident (throws error)
queries[110] = '-is:retweet ((school (shooting OR shootings)) OR (Brooklyn (shooting OR shootings)))'
# Remove school name from 246th incident (throws error)
queries[246] = '-is:retweet ((school (shooting OR shootings)) OR (Middletown (shooting OR shootings)))'
# And other incidents...
queries[281] = '-is:retweet ((school (shooting OR shootings)) OR (Albuquerque (shooting OR shootings)))'

# In order to address these exceptions more dynamically than waiting for errors, I have adjusted the list of schools above



# DEFINE FUNCTIONS FOR API REQUESTS
def generate_url(query, start_time, end_time, max_results=500, next_token=False):
    if (next_token == False):
        url = "https://api.twitter.com/2/tweets/search/all?query={}&start_time={}&end_time={}&tweet.fields=text,author_id,created_at,geo,lang&max_results={}".format(query, start_time, end_time, max_results)
    else:
        url = "https://api.twitter.com/2/tweets/search/all?next_token={}&query={}&start_time={}&end_time={}&tweet.fields=text,author_id,created_at,geo,lang&max_results={}".format(next_token, query, start_time, end_time, max_results)
    return url

headers = {"Authorization": "Bearer {}".format(bearer_token)}

def search_twitter(url):
    response = requests.request("GET", url, headers=headers)

    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()

# Initialize counter variables
num_requests = 0
num_results = 0

# Specify relative filepath for outputs
# Because we are getting so much data, we are saving it outside the GitHub repository
rel_filepath = "../../../../../excess_data/00-raw-data/Twitter/"

# Set maximum number of tweets per incident
max_inc_results = 7500

# 2 limits:
# 1. 300 requests / 15 min
# 2. 1 request / sec

# Use this variable to pick up progress in case errors occur
start_id = 0

# BEGIN API REQUESTS
for i, (inc_id, query, start_t, end_t) in enumerate(zip(ids[start_id:], queries[start_id:], start_times[start_id:], end_times[start_id:])):
    # Print status
    print("Requesting tweets for incident ID " + inc_id + "...")

    # Initialize tracking variables
    next_page = True # Track pagination
    num_page = 0 # Track pagination numbers
    nt = False # Set nt (next token) as False for first request of query

    # Start "timers" for regulation of limits
    limit1_start = time.time() # Do not exceed 300 requests / 15 min
    limit2_start = time.time() # Do not exceed 1 request / second

    while (next_page == True):
        # Generate URL (nt will be false on first and last requests of the query)
        query_url = generate_url(query=query, start_time=start_t, end_time=end_t, max_results=500, next_token=nt)


        # Make request (include try-except and while loop to handle Exception errors)
        # See the link below for explanation of this code
        # https://stackoverflow.com/questions/2083987/how-to-retry-after-exception
        while True:
            try:
                json_response = search_twitter(url=query_url)
            except Exception:
                # If Exception error occurs, sleep two minutes
                print("Exception occurred: 2 minute sleep")
                for sec in tqdm(range(2*60)):
                    time.sleep(1)
                continue
            break

        # Track metadata
        num_results = num_results + json_response['meta']['result_count']
        try:
            nt = json_response['meta']['next_token']
            num_page += 1
        except KeyError:
            nt = False
            next_page = False
            print(str(num_results) + " tweets saved (all retrieved)")
            num_results = 0


        # Track progress
        num_requests += 1

        # Save response
        output = json.dumps(json_response, indent=4, sort_keys=True)

        with open(rel_filepath + inc_id + '_' + str(num_page) + '.json', 'w') as outfile:
            outfile.write(output)

        # Check limits
        # Limit 1: 300 requests / 15 min
        if (num_requests >= 200) or ((time.time() - limit1_start) > 10*60):
            # Sleep ten minutes (1 request / sec for 300 requests is 5 min)
            print("15 minute sleep")
            for sec in tqdm(range(15*60)):
                time.sleep(1)
            
            # Reset request count and "timer"
            num_requests = 0
            limit1_start = time.time()

        # Limit 2: 1 request / sec
        if (time.time() - limit2_start <= 1):
            time.sleep(1) # Add extra second for good measure

        limit2_start = time.time() # Reset "timer"

        # Check if tweet count has exceeded max_inc_results
        if (max_inc_results < num_results):
            next_page = False
            print(str(num_results) + " tweets saved (limit capped)")
            num_results = 0
        


print("All requests complete.")




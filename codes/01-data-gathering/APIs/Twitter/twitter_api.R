# Load libraries
library(rjson)
library(rtweet)

# Set up Twitter token
api_keys <- fromJSON(file = "~/Coding/Keys/twitter.json")$DSAN

twitter_token <- create_token(
  app = api_keys$app,
  consumer_key = api_keys$key,
  consumer_secret = api_keys$key_secret,
  access_token = api_keys$access_token,
  access_secret = api_keys$access_token_secret
)


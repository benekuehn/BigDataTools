import tweepy
import csv
from datetime import datetime

# Twitter API credentials
consumer_key = ""
consumer_secret = ""

# pass twitter credentials to tweepy
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
api = tweepy.API(auth)

Collected_data = []

#name of twitter account
screen_name = ""

#number of tweets
tweets_max = 3000

#how many tweets per API request, default 200
tweets_per_call = 200

if tweets_max > tweets_per_call:
    print("More tweets then I can get per call")
    new_tweets = api.user_timeline(
        screen_name=screen_name, count=tweets_per_call, tweet_mode="extended")

elif tweets_max < tweets_per_call:
    print("Less tweets then I can get per call")
    tweets_per_call = tweets_max
    new_tweets = api.user_timeline(
        screen_name=screen_name, count=tweets_per_call, tweet_mode="extended")

Collected_data.extend(new_tweets)

oldest = Collected_data[-1].id - 1

tweets_collected = tweets_per_call
tweets_needed = tweets_max - tweets_collected

print("Still %s tweets to go" % tweets_needed)

while tweets_needed != 0:

    if tweets_needed < tweets_per_call:
        tweets_needed = tweets_per_call

    new_tweets = api.user_timeline(
        screen_name=screen_name, count=tweets_needed, max_id=oldest, tweet_mode="extended")

    # wait_on_rate_limit=True

    tweets_needed = tweets_needed - tweets_per_call

    print("Still %s tweets to go" % tweets_needed)

    Collected_data.extend(new_tweets)

    oldest = Collected_data[-1].id - 1


# print(Collected_data)

    outtweets = [[tweet.id,
                  tweet.user.screen_name,
                  tweet.created_at,
                  tweet.favorite_count,
                  tweet.retweet_count,
                  tweet.source,
                  tweet.full_text,
                  # tweet.entities["user_mentions"], // Just in case to memorize how it works
                  tweet.in_reply_to_user_id,
                  # tweet.author.screen_name, // Just in case to memorize how it works
                  ] for tweet in Collected_data if (datetime.now() - tweet.created_at).days > 1] # Only processing tweets which are older then 1 day


i = 0
has_writer = False
for tweet in Collected_data:

    # Only processing tweets which are older then 1 day
    if (datetime.now() - tweet.created_at).days > 1:

        if hasattr(tweet, "retweeted_status"):
            outtweets[i].append(1)
        else:
            outtweets[i].append(0)

        if tweet.is_quote_status == True:
            outtweets[i].append(1)
        else:
            outtweets[i].append(0)

        try:
            "url" in tweet.entities["urls"][0]
            outtweets[i].append(1)

        except IndexError:
            outtweets[i].append(0)

        if "media" in tweet.entities:
            if "media" in tweet.extended_entities:
                outtweets[i].append(1)
        else:
            outtweets[i].append(0)

        if "^" in tweet.full_text:
            writer = tweet.full_text.split("^", 1)[1]  # Splits Str at ^
            # Splits Str again after space to seperate only! two character abbreviation for writer
            writer = writer.split(" ", 1)[0]
            outtweets[i].append(writer)
            has_writer = True
        i += 1


# print(outtweets)

now = datetime.now()
dt_string = now.strftime("%d-%m-%Y-%H-%M-%S")

file_name = "tweets_%s_%s.csv" % (screen_name, dt_string)

# helps to only include writer column in csv only when there is a writer like in my united case.
if has_writer == True:
    with open(file_name, "w",) as f:
        writer = csv.writer(f)
        writer.writerow(["tweet_id",
                         "username",
                         "created_at",
                         "favorite_count",
                         "retweet_count",
                         "source",
                         "full_text",
                         "in_reply_to_user_id",
                         "is_retweeted",
                         "is_quote_status",
                         "has_url",
                         "has_media",
                         "writer"]
                        )
        writer.writerows(outtweets)

    pass
else:
    with open(file_name, "w",) as f:
        writer = csv.writer(f)
        writer.writerow(["tweet_id",
                         "username",
                         "created_at",
                         "favorites",
                         "retweets",
                         "source",
                         "text",
                         "in_reply_to_user_id",
                         "is_retweeted",
                         "is_quote_status",
                         "has_url",
                         "has_media", ]
                        )
        writer.writerows(outtweets)
    pass
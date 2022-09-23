from tweepy.streaming import Stream
from kafka import KafkaProducer
import json
import time
import configparser
import sys

keyword = sys.argv

key = []
key.append(keyword[1])
# print(key)

class StdOutListener(Stream):
    def __init__(self,consumer_key,consumer_secret,access_token,access_token_secret, verify):
        super().__init__(consumer_key,consumer_secret,access_token,access_token_secret, verify = verify)

    def on_data(self, raw_data):
        producer.send('keyword_stream', raw_data)
        # producer.flush()
        return True
    def on_error(self, status):
        print (status)
    def on_limit(self,status):
        print ("Twitter API Rate Limit")
        print("Waiting...")
        time.sleep(15 * 60)
        print("Resuming")
        return True

if __name__ == '__main__':

    config = configparser.ConfigParser()
    config.read('twitter_creds.ini')
    consumer_key = config['DEFAULT']['consumer_key']
    consumer_secret = config['DEFAULT']['consumer_secret']
    access_token = config['DEFAULT']['access_token']
    access_token_secret = config['DEFAULT']['access_token_secret']

    producer = KafkaProducer(bootstrap_servers='localhost:9092')
    myStream = StdOutListener(consumer_key,consumer_secret,access_token,access_token_secret, verify = False)

    myStream.filter(track=key, languages=["en"])

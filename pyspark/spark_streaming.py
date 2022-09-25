import findspark 
findspark.init("/Users/smacherla/Downloads/kafka_twitter_project_py_3.7/spark-2.4.3-bin-hadoop2.7")
import os
import sys
os.environ['PYSPARK_PYTHON'] = sys.executable
os.environ['PYSPARK_DRIVER_PYTHON'] = sys.executable
os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.4.3 pyspark-shell'
import pyspark
from pyspark import SparkContext, SparkConf, StorageLevel
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
from kafka import KafkaProducer
import json
import numpy
from textblob import TextBlob
import re
import requests


def bounding_box(coordinates):
    coords = str(coordinates)
    coords = coords.replace("[", "")
    coords = coords.replace("]", "")
    coords = coords.replace(",", "")
    coords = coords.replace("'", "")
    coords_list = coords.split(" ")
    x1 = float(coords_list[0])
    y1 = float(coords_list[1])
    x2 = float(coords_list[2])
    y2 = float(coords_list[3])
    x3 = float(coords_list[4])
    y3 = float(coords_list[5])
    x4 = float(coords_list[6])
    y4 = float(coords_list[7])

    long = (x1 + x2 + x3 + x4)/4
    lat = (y1 + y2 + y3 + y4)/4
    return (lat, long)


def cleanTweet(tweet_json):
    # checking if the tweet is extended or not
    if tweet_json['truncated'] == False:
      tweet = str(tweet_json['text'])
    else:
      tweet = str(tweet_json['extended_tweet']['full_text'])
    
    # stripping the https link from the tweet text
    tweet = re.sub(r'http\S+', ' ', str(tweet))
    tweet = re.sub(r'bit.ly/\S+', ' ', str(tweet))
    tweet = tweet.strip('[link]')

    # removing tagged users
    tweet = re.sub('(RT\s@[A-Za-z]+[A-Za-z0-9-_]+)', ' ', str(tweet))
    tweet = re.sub('(@[A-Za-z]+[A-Za-z0-9-_]+)', ' ', str(tweet))

    # removing puntuation
    my_punctuation = '!"$%&\'()*+,-./:;<=>?[\\]^_`{|}~•@â'
    tweet = re.sub('[' + my_punctuation + ']+', ' ', str(tweet))

    # to remove any numbers from the tweet
    tweet = re.sub('([0-9]+)', ' ', str(tweet))

    # to remove any non-ascii characters
    tweet = tweet.encode("ascii", "ignore")
    tweet = tweet.decode()

    # to remove emojis 
    def remove_emoticons(data):
      emoticons = re.compile("["
          u"\U0001F600-\U0001F64F"  # emoticons
          u"\U0001F300-\U0001F5FF"  # symbols & pictographs
          u"\U0001F680-\U0001F6FF"  # transport & map symbols
          u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
          u"\U000024C2-\U0001F251"
          u"\U0001f926-\U0001f937"
          u"\U00010000-\U0010ffff"
          u"\u2600-\u2B55"
          u"\u200d"
          u"\u23cf"
          u"\u23e9"
          u"\u231a"
          u"\ufe0f"
          u"\u3030"
                        "]+", re.UNICODE)
      return re.sub(emoticons,' ', data)

    # removing \n characters from the tweet string
    tweet = remove_emoticons(tweet)
    tweet = tweet.replace("\n", " ")

    return tweet

def tweet_sentiment(text):
  text = str(text)
  polarity = round(float(TextBlob(text).sentiment.polarity),2) 
  if polarity > 0.10:
    if polarity > 0.60: 
      return (polarity, 'very positive')
    else:
      return (polarity, 'positive')
  elif polarity < -0.10: 
    if polarity < -0.60:
      return (polarity, 'very negative')
    else:
      return (polarity, 'negative')
  else:
    return (polarity, 'neutral')

def kafka_sender(messages):

    producer = KafkaProducer(bootstrap_servers='localhost:9092')

    for message in messages:
        message = str(message)
        producer.send('twitter_sentiment_stream', bytes(message, 'utf-8'))
    producer.flush()


interval = 2 # to check for tweets every 2 seconds

topic = 'kafka_twitter_stream_json' 

conf = SparkConf().setAppName("KafkaTweetStream").setMaster("local[*]")
sc = SparkContext(conf=conf)
sc.setLogLevel("WARN")
ssc = StreamingContext(sc, interval)

kafkaStream = KafkaUtils.createDirectStream(ssc, [topic], {
  'bootstrap.servers': 'localhost:9092', 'group.id': 'twitter',
  'fetch.message.max.bytes': '15728640',
  'auto.offset.reset': 'largest'}) 

'''
        Tweets are coming in from the Kafka topic in large json blocks, extract the username, location
        and contents of the tweets as json objects.

        Basic dataframe for analysis.
'''

tweets = kafkaStream. map(lambda value: json.loads(value[1])). \
  map(lambda json_object: (json_object["user"]["screen_name"], 
    bounding_box(json_object["place"]["bounding_box"]["coordinates"]),
      cleanTweet(json_object), tweet_sentiment(cleanTweet(json_object))))
                    
tweets.pprint(10)
tweets.persist(StorageLevel.MEMORY_AND_DISK) 


"""process the tweets further to extract hashtag from the tweet text and count it in a window of 24 hours every 2 seconds"""

trending = tweets.map(lambda value: (value[0], value[2])).flatMapValues(lambda value: value.split(" ")).\
                  filter(lambda word: len(word[1]) > 1 and word[1][0] == '#'). \
                  map(lambda hashtag: (hashtag[1], 1)).\
                    reduceByKeyAndWindow(lambda a, b: a+b, None, 60*60*24, 2). \
                      transform(lambda rdd: rdd.sortBy(lambda a: -a[-1]))
                      

def trending_to_flask(rdd):
    '''
    For each RDD send top ten data to flask api endpoint
    '''
    if not rdd.isEmpty():
        top = rdd.take(10)

        labels = []
        counts = []

        for label, count in top:
            labels.append(label)
            counts.append(count)

            request = {'label': str(labels), 'count': str(counts)}
            response = requests.post('http://0.0.0.0:5001/update_trending', data=request)

trending.pprint(10) 
trending.foreachRDD(trending_to_flask) 

"""process the tweets to extract coordinates and sentiment to push to a new kafka topic to plot them on the map in real-time"""

sentiment = tweets. \
  map(lambda value: (value[1], value[3]))

sentiment.pprint() 
sentiment.foreachRDD(lambda rdd: rdd.foreachPartition(kafka_sender))

''' 
  process the stream from keyword-stream topic and analyze it to
  create a bar chart similar to the trending function to show the number of sentiments 
  for the keyword specified
'''

topic = 'keyword_stream'

keywordStream = KafkaUtils.createDirectStream(ssc, [topic], {
  'bootstrap.servers': 'localhost:9092', 'group.id': 'twitter',
  'fetch.message.max.bytes': '15728640',
  'auto.offset.reset': 'largest'}) 

keywords = keywordStream.map(lambda value: json.loads(value[1])).map(lambda json_object: (json_object["user"]["screen_name"],cleanTweet(json_object), tweet_sentiment(cleanTweet(json_object))))
keywords.persist(StorageLevel.MEMORY_AND_DISK)

keywords_further_process = keywords.map(lambda value: (value[0], value[2])).map(lambda sentiment: (sentiment[1][1], 1)).\
                                      reduceByKeyAndWindow(lambda a, b: a+b, None, 60*60*24, 2). \
                                        transform(lambda rdd: rdd.sortBy(lambda a: -a[-1]))


def keyword_sentiment_to_flask(rdd):
    '''
    For each RDD send top ten data to flask api endpoint
    '''
    if not rdd.isEmpty():
        top = rdd.take(5)

        labels = []
        counts = []

        for label, count in top:
            labels.append(label)
            counts.append(count)
            request = {'label': str(labels), 'count': str(counts)}
            response = requests.post('http://0.0.0.0:5001/update_keyword', data=request)

keywords_further_process.pprint(10) 
keywords_further_process.foreachRDD(keyword_sentiment_to_flask) 


ssc.start() 
ssc.awaitTermination() 

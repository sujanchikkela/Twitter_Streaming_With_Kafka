# Real-time Twitter Streaming and Sentiment Analysis
<img alt="image" src="https://cdn.vox-cdn.com/thumbor/BJvHEuVBOfwf98qRI8jFsrDoyC8=/0x0:1000x667/1000x667/filters:focal(500x334:501x335):no_upscale()/cdn.vox-cdn.com/uploads/chorus_asset/file/10262551/mdoying_180117_2249_twitter_rocking.gif">


## Problem Statement

This project aims to design and implement a data intensive software application to acquire, store, process and visualise analytics from real-time live tweets generated across different countries. The application makes use of common distributed computing technologies for working with large volumes of data at scale (Apache Kafka, Apache Spark), and web frameworks (Flask, JavaScript) for the visualisation of the data. The project also makes use of AWS to aid development and deployment.

## Abstract

Goal of this project is to connect to Twitter API and continuously stream tweets of a specific location or keyword and then to perform real-time processing on the streamed tweets on the fly to calculate sentiment analysis based on the tweet text, and eventually visualize the results real-time.

One of the requirement to work with twitter API, is to get access to twitter developer account with elevated privileges.

## Persona

The project is targeted towards people who wants to analyze the overall sentiments of real-time streaming twitter data filtered by a specific 
location or keyword and also one can check whats trending in a specific country. (Stream real-time tweets and observe the sentiments related to any particular topic and can get the insights about people's opinion accordingly plan product improvements)

## Project Outline

The development of an end to end soultion comprised of:

* Scalable data pipelines to stream and store real time tweets of specific keyword and across different locations, using Apache Kafka(Producer API, Twitter API).
* Scalable processing of the live tweets collected and sentiment analysis of each tweet that comes in, using Apache Spark Pyspark data processing and textblob python libraries.
* A web front end to display the results of the sentiments, running total of top ten Hashtags, map of a specific location showing sentiment of tweets,       using Flask and JavaScript libraries.

## Technologies and Resources 🖥
[![](https://img.shields.io/badge/Twitter-API-FFD43B?style=for-the-badge&logo=python&logoColor=darkgreen)](https://www.python.org)  [![](https://img.shields.io/badge/Kafka-FF6F00?style=for-the-badge&logo=kafka&logoColor=white)](https://www.tensorflow.org) [![](https://img.shields.io/badge/Spark-F7931E?style=for-the-badge&logo=spark-learn&logoColor=white)](https://scikit-learn.org/stable/) [![](https://img.shields.io/badge/Flask-654FF0?style=for-the-badge&logo=flask&logoColor=white)](https://www.scipy.org) [![](https://img.shields.io/badge/HTML-777BB4?style=for-the-badge&logo=html&logoColor=white)](https://numpy.org)

## Python Libraries

Tweepy, pyspark, kafka-python, Textblob, numpy, requests

## Project Architecture

The design architecture for the project is as shown: 

<img width="861" alt="image" src="https://user-images.githubusercontent.com/98585812/166820593-7fcb3f96-292a-4202-9559-bc1705562d98.png">

## Project Implementation

### Stage 1: Data Ingestion
Tweepy and Kafka Python libraries are used to pull tweets as JSON objects and to create ‘streams’ of tweets into two separate Kafka topics(two producer scripts). The first topic will take all available tweet objects created across different locations and will be used to analyse the running trending topic and tagged users and the second topic will take all the available tweets of particular keyword. 

### Stage 2: Data Processing and Sentiment Analysis
The two Kafka topics ‘produced’ in the previous stage are ‘consumed’ by the data processing stage. This stage utilises Apache Spark to create the running total dataframes and, in combination with the TextBlob library will ‘produce’ a new Kafka topic stream of tweet coordinates and sentiment levels. The three dataframes will be pushed to the front-end at regular 2 second intervals. The separate tweet sentiment stream will be ‘consumed’ during the visualisation stage.

### Stage 3: Sentiments Visualisation (Keyword sentiments and location based sentiments)
The final stage is the creation of the web front end and visualisations. A python Flask app is created to route and collect data directly from Spark and the produced Kafka sentiment stream. Bootstrap and CSS will be implemented to create a consistent interface to ‘store’ the two visualisations. The two running total charts is produced with Chart.js with the sentiment map created with Leaflet.js.


## Demo screenshots

* Get started html page sends input to flask which intern sends to kafka producer scripts to start streaming.

* Trending.html receive top 10 hashtags from spark, which gets updated automatically as the new tweets coming into spark from kafka.
<img width="600" alt="image" src="https://user-images.githubusercontent.com/98585812/166879182-85f1d217-4386-497a-9446-2b2821029fab.png">

* Refresh_trending API endpoint which sends the data to trending.html!
<img width="600" alt="image" src="https://user-images.githubusercontent.com/98585812/166879247-2881ec37-8a29-47b6-8c05-a9bc1ce21332.png">

* Location based sentiments which gets updated as the new tweets coming in to kafka topic “twitter_sentiment_stream”
<img width="600" alt="image" src="https://user-images.githubusercontent.com/98585812/166879309-70b79ab8-ac31-4329-8362-821cee1df327.png">

* Sentiments console output based on location(co-ordinates, polarity and Sentiment)
<img width="600" alt="image" src="https://user-images.githubusercontent.com/98585812/166879382-c99cc199-546e-4eb5-9dae-aa7114d893b8.png">

* Sentiments based on keyword
<img width="600" alt="image" src="https://user-images.githubusercontent.com/98585812/166879437-d1bbb287-c5cb-4e91-9423-0f27d4921619.png">

* Refresh_keyword API endpoint which sends the data to keyword.html
<img width="468" alt="image" src="https://user-images.githubusercontent.com/98585812/166879490-141266d0-c7d0-4a87-ab1c-5f232b1ccbcc.png">

* Spark console output:
<img width="600" alt="image" src="https://user-images.githubusercontent.com/98585812/166879568-33de7473-2e22-476d-82e5-9bfe66eee265.png">


##
### Project Setup

* #### Installing Required Python Libraries I have provided a text file containing the required python packages: requirements.txt

        To install all of these at once, simply run (only missing packages will be installed):
        $ sudo pip install -r requirements.txt

* #### Installing and Initializing Kafka Download and extract the latest binary from https://kafka.apache.org/downloads.html

* ##### Start zookeeper service:

        $ bin/zookeeper-server-start.sh config/zookeeper.properties

* ##### Start kafka service: 

        $ bin/kafka-server-start.sh config/server.properties

* ##### Create a topic 

        $ /bin/kafka-topics.sh --create --bootstrap-servers localhost:9092 --replication-factor 1 --partitions 1 --topic {topic name of your choice} 
 
##

* #### Using the Twitter Streaming API In order to download the tweets from twitter streaming API and push them to kafka queue, I have created a python script location_streaming.py and keyword_streaming.py, the script will need your twitter authentication tokens (keys).

          Once you have your authentication tokens, create or update the twitter-app-credentials.txt with these credentials. 
          After updating the text file with your twitter keys, you can start downloading tweets from the twitter stream API 
          and push them to the topic in Kafka. Do this by running the script as follows:
        
          $ python tweets_extraction.py
          Note: This program should be kept running for collecting tweets.

##

* ##### To check if the data is landing in Kafka: 

         $ ./bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic {topic_name} [—from beginning]

* ##### Running the Stream Analysis Program: 

        In order to run the spark script, you should have java 8 installed.
        As the project is mainly focused on live streaming of tweets, kafka producer, spark processing; kafka and zookeeper should be kept running in the  background or as containers. 


from flask import Flask, jsonify, request, Response, render_template
from pykafka import KafkaClient
import ast
import subprocess
import os
import signal
import time

def get_kafka_client():
    return KafkaClient(hosts='localhost:9092')

app = Flask(__name__)

trending = {'labels': [], 'counts': []}
keyword = {'labels': [], 'counts': []}

@app.route("/")
def get_about_page():
    	
	return render_template('Home.html')

@app.route("/input.html", methods=['GET', 'POST'])
def get_dashboard_page():

	global keyword_pid
	global location_pid
	global spark_pid

	country_name = []

	with open('country-boundingboxes.csv') as file:
		for line in file:
			if line.rstrip().split(',')[0] != 'country':
				country_name.append(line.rstrip().split(',')[0])
	if request.method == "POST":
		if request.form['Submit'] == 'Submit':
			"""get input from the GUI"""
			fname = str(request.form['fname'])
			cname = str(request.form['country_name'])

			"""run tweets streaming and spark analysis based on the input given"""

			with open('keyword_streaming_log.txt', 'w') as x:
				keyword_pid = subprocess.Popen(["nohup","python", "/home/ubuntu/kafka_twitter_project_py_3.7/kafka_py/keyword_streaming.py", fname, "&"], stdout=x)
			with open('location_streaming_log.txt', 'w') as y:
				location_pid = subprocess.Popen(["nohup","python", "/home/ubuntu/kafka_twitter_project_py_3.7/kafka_py/location_streaming.py", cname, "&"], stdout=y)
			with open('spark_log.txt', 'w') as z:
				spark_pid = subprocess.Popen(["nohup","python", "/home/ubuntu/kafka_twitter_project_py_3.7/pyspark/spark_streaming.py",  "&"], stdout=z)

		elif request.form['Submit'] == 'Reset':
			"""to kill the streaming instances and spark analysis as soon as Reset is hit"""
		
			os.kill(keyword_pid.pid, 9)
			time.sleep(3)
			os.kill(location_pid.pid, 9)
			time.sleep(3)
			os.kill(spark_pid.pid, 9)
			time.sleep(3)
			subprocess.run(["sh","/home/ubuntu/kafka_twitter_project_py_3.7/kafka_2.13-3.0.1/bin/kafka-topics.sh", "--bootstrap-server", "localhost:9092", "--delete", "--topic", "twitter_sentiment_stream"])
			time.sleep(2)
			subprocess.run(["sh","/home/ubuntu/kafka_twitter_project_py_3.7/kafka_2.13-3.0.1/bin/kafka-topics.sh", "--bootstrap-server", "localhost:9092", "--delete", "--topic", "kafka_twitter_stream_json"])
			time.sleep(2)
			subprocess.run(["sh","/home/ubuntu/kafka_twitter_project_py_3.7/kafka_2.13-3.0.1/bin/kafka-topics.sh", "--bootstrap-server", "localhost:9092", "--delete", "--topic", "keyword_stream"])
			time.sleep(2)
			subprocess.run(["sh","/home/ubuntu/Downloads/kafka_twitter_project_py_3.7/kafka_2.13-3.0.1/bin/kafka-topics.sh", "--bootstrap-server", "localhost:9092", "--create", "--topic", "twitter_sentiment_stream"])
			time.sleep(2)
			subprocess.run(["sh","/home/ubuntu/Downloads/kafka_twitter_project_py_3.7/kafka_2.13-3.0.1/bin/kafka-topics.sh", "--bootstrap-server", "localhost:9092", "--create", "--topic", "kafka_twitter_stream_json"])
			time.sleep(2)
			subprocess.run(["sh","/home/ubuntu/Downloads/kafka_twitter_project_py_3.7/kafka_2.13-3.0.1/bin/kafka-topics.sh", "--bootstrap-server", "localhost:9092", "--create", "--topic", "keyword_stream"])
			time.sleep(2)

	return render_template(
		'input.html',
		country_name=country_name)
 
@app.route('/topic/<topicname>')
def get_messages(topicname):
    client = get_kafka_client()
    def events():
        for x in client.topics[topicname].get_simple_consumer():
            yield 'data:{0}\n\n'.format(x.value.decode())
    return (Response(events(), mimetype="text/event-stream"))  

@app.route("/trending.html")
def get_hashtags_page():
    global trending
    
    return render_template('trending.html',
    trending=trending)

@app.route("/map.html")
def get_map():
    return(render_template('map.html'))


@app.route('/refresh_trending')
def refresh_trending():
	global trending

	return jsonify(
		Label=trending['labels'],
		Count=trending['counts'])

@app.route('/update_trending', methods=['POST'])
def update_trending():
	global trending
	if not request.form not in request.form:
		return "error", 400

	trending['labels'] = ast.literal_eval(request.form['label'])
	trending['counts'] = ast.literal_eval(request.form['count'])

	return "success", 201


@app.route("/keyword.html")
def get_keywords_page():
    global keyword
    
    return render_template('keyword.html',
    keyword=keyword)

@app.route('/update_keyword', methods=['POST'])
def update_keyword():
	global keyword
	if not request.form not in request.form:
		return "error", 400

	keyword['labels'] = ast.literal_eval(request.form['label'])
	keyword['counts'] = ast.literal_eval(request.form['count'])

	return "success", 201

@app.route('/refresh_keyword')
def refresh_keyword():
	global keyword

	return jsonify(
		Label=keyword['labels'],
		Count=keyword['counts'])



if __name__ == "__main__":
	app.run(debug=True,host='0.0.0.0', port=5001)

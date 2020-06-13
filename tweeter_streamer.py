
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler, Stream, API, Cursor

import app_credentials
import os
import re
import sys
import threading, time
import boto3
from tqdm import tqdm

class StdOutListener(StreamListener):

	def __init__(self, path, filename, time_limit):
		super(StdOutListener, self).__init__()
		self.start_time = time.time()
		self.limit = time_limit
		self.path = path
		self.filename = filename
		self.id = 0
	
	def on_status(self, data):
		if (time.time() - self.start_time) < self.limit:
			if self.id == 0:
				with open(self.path+self.filename, 'w', encoding="utf-16") as f:
					f.write("id,comment,creation_time,source,tweet_id,user,user_id\n")
					f.write("%s,%s,%s,%s,%s,%s,%s\n" % (self.id, re.sub(r'[,\n]',' ', data.text), data.created_at, data.source.replace(',', ' '), data.id_str, data.user.name.replace(',', ' '), data.user.id_str))
			else:
				with open(self.path+self.filename, 'a', encoding="utf-16") as f:
					f.write("%s,%s,%s,%s,%s,%s,%s\n" % (self.id, re.sub(r'[,\n]',' ', data.text), data.created_at, data.source.replace(',', ' '), data.id_str, data.user.name.replace(',', ' '), data.user.id_str))

			self.id = self.id + 1
			#print(data.text)
			return True
		else:
			return False

	def on_error(self, status):
		if status == 401:
			print(status)
			return False

		print(status)
		return False

def background(stream):
	stream.filter(track = ['George Floyd', 'Donald Trump', 'BlackLivesMatters', 'Bryanna Taylor', 'Police'], languages = ['en'], is_async=True)

def wait(minutes):
	for i in tqdm(range(60*minutes)):#five minutes
		time.sleep(1)  #update each second


if __name__ == '__main__':
	MINUTES = 30
	FILE_PATH = './'
	FILE_NAME = 'comments.csv'

	listener = StdOutListener(FILE_PATH, FILE_NAME,60*MINUTES)
	#listener = StdOutListener()
	auth = OAuthHandler(app_credentials.CONSUMER_KEY, app_credentials.CONSUMER_SECRET)
	auth.set_access_token(app_credentials.ACCESS_TOKEN, app_credentials.ACCESS_TOKEN_SECRET)
	api = API(auth)
	
	stream = Stream(api.auth, listener)

	try:
		background(stream)
		#tweet_capturer = threading.Thread(name = 'background', target = background, args=[stream])
		#tweet_capturer.start()
		wait(MINUTES)
	except:
		stream.disconnect()

	#after creation of file publish to s3
	print("Publicando a bucket")
	S3_BUCKET = "cmurill5tmp"
	s3_client = boto3.client('s3')

	s3_client.upload_file(FILE_PATH+FILE_NAME,S3_BUCKET,FILE_NAME)


	#finaliza ejecucion
	print("Ejecución terminada")



	



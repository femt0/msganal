import logging
import re
import emoji
import config
import model
from fbchat import Client
from operator import itemgetter
from datetime import datetime
from textblob import Blobber
from celery import task  
from textblob_fr import PatternTagger, PatternAnalyzer
from flask_socketio import SocketIO

class AnalyticsClient(Client):
	def onMessage(self, author_id, message_object, thread_id, thread_type, **kwargs):
		print(message_object)
		#process_message(message_object, thread_id)

	def on2FACode(self):
		#Sleep 10s on 2FA code request -> let the time to authorize via fb mobile notification
		time.sleep(10)
		return

#global thread_id, blobber #, celery
#celery = Celery(current_app.name, broker=current_app.config['CELERY_BROKER_URL'])  
#celery.conf.update(current_app.config) 
blobber = Blobber(pos_tagger=PatternTagger(), analyzer=PatternAnalyzer())
cookies = eval(str(model.get_cookies(config.THREAD_ID)))
client = AnalyticsClient(config.MESSENGER_USERNAME, config.MESSENGER_PASSWORD, session_cookies=cookies)
model.set_cookies(config.THREAD_ID, str(client.getSession())) 

local_socketio = SocketIO(message_queue=config.REDIS_EXCHANGE_URL)

@task()
def start():
	client.listen()

@local_socketio.on('stop_listening', namespace='/socket')
def stop():
	client.stopListening()

@task()
def scan(after, before, flush=False):
	#init redis
	if flush:
		model.flushall()
		model.set_cookies(config.THREAD_ID, str(client.getSession()))

	while True:
		try:
			messages = client.fetchThreadMessages(thread_id=config.THREAD_ID, before=before)
		except:
			#PARAM
			before = int(before) - 60000
			print("\n\n\nERROR: SKIP A MINUTE\n\n\n")
			continue

		if not messages:
			#log
			break

		#log
		print('\n\n\n')
		print(datetime.now())
		print(datetime.fromtimestamp(int(messages[-1].timestamp)/1000))

		for message in messages:
			if int(message.timestamp) >= after:
				process_message(message)

		local_socketio.emit('refresh_messages', 'refresh_messages')
		local_socketio.emit('refresh_stickers', model.get_stickers())

		before = int(messages[-1].timestamp)-1
		if before < after:
			break

def process_message(message):
	#condition on expected thread
	print(message)
	userid = message.author
	global_not_exists = model.upsert_user(config.GLOBAL)
	user_not_exists = model.upsert_user(userid)
						
	if global_not_exists:
		info = client.fetchThreadInfo(config.THREAD_ID)[config.THREAD_ID]
		model.update_user_info(config.GLOBAL, info.name, info.photo)
	
	if user_not_exists:
		info = client.fetchUserInfo(userid)[userid]
		model.update_user_info(userid, info.first_name, info.photo)

	model.increment_user_msg(config.GLOBAL)
	model.increment_user_msg(userid)

	#photos
	for attach in message.attachments:
		if type(attach).__name__ == 'ImageAttachment':
			model.increment_user_img(config.GLOBAL)
			model.increment_user_img(userid)

	#time
	dt = datetime.fromtimestamp(int(message.timestamp)/1000)
	model.update_user_times(config.GLOBAL, dt)
	model.update_user_times(userid, dt)

	text = message.text
	if text:
		model.increment_user_txt(config.GLOBAL)
		model.increment_user_txt(userid)
		#words
		words = get_valid_words(text)
		model.update_user_words(config.GLOBAL, words)
		model.update_user_words(userid, words)
		#emojis
		emojis = get_emojis(text)
		model.update_user_emojis(config.GLOBAL, emojis)
		model.update_user_emojis(userid, emojis)
		#average size
		size = len(text)
		model.update_user_average_size(config.GLOBAL, size)
		model.update_user_average_size(userid, size)
		#polarity
		polarity = get_polarity(text)
		model.update_user_average_polarity(config.GLOBAL, polarity)
		model.update_user_average_polarity(userid, polarity)

	#stickers
	if message.sticker:
		model.update_user_stickers(config.GLOBAL, message.sticker)
		model.update_user_stickers(userid, message.sticker)

def get_valid_words(text):
	words = re.split(r'[ .,:!?-_()/;\n\'\"]', text.lower())
	words = [str(w) for w in words if w in config.VALIDWORDS]
	return words

def get_emojis(text):
	emojis_list = map(lambda x: ''.join(x.split()), emoji.UNICODE_EMOJI.keys())
	r = re.compile('|'.join(re.escape(p) for p in emojis_list))
	return r.findall(text)

def get_polarity(text):
	tb = blobber(text)
	return float(tb.sentiment[0])


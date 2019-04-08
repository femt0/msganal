from flask import current_app
import config
import redis

r = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_APP_DB, charset="utf-8", decode_responses=True)

def get_cookies(threadid):
	return r.get('thread:{}:cookies'.format(threadid))

def set_cookies(threadid, cookies):
	r.set('thread:{}:cookies'.format(threadid), cookies)

def flushall():
	r.flushall()

def upsert_user(userid):
	return r.sadd('users', userid)

def update_user_info(userid, name, imgurl):
	r.set('user:{}:name'.format(userid), name)
	r.set('user:{}:imgurl'.format(userid), imgurl)

def increment_user_msg(userid):
	r.incr('user:{}:cntmsg'.format(userid))

def increment_user_txt(userid):
	r.incr('user:{}:cnttxt'.format(userid))

def increment_user_img(userid):
	r.incr('user:{}:cntimg'.format(userid))

def update_user_emojis(userid, emojis):
	r.incrby('user:{}:cntemj'.format(userid), len(emojis))
	for e in emojis:
		r.zincrby('user:{}:emojis'.format(userid), 1, e)

def update_user_words(userid, words):
	for w in words:
		r.hincrby('user:{}:words'.format(userid), w)

def update_user_stickers(userid, sticker):
	r.incr('user:{}:cntstk'.format(userid))
	r.zincrby('user:{}:stickers'.format(userid), 1, sticker.uid)
	exists = r.sadd('stickers', sticker.uid)
	if not exists:
		r.set('sticker:{}:imgurl'.format(sticker.uid), sticker.url)

def update_user_average_size(userid, size, diff=-1):
	avgsize = r.get('user:{}:avgsize'.format(userid))
	if avgsize:
		cnttxt = r.get('user:{}:cnttxt'.format(userid))
		if cnttxt:
			r.set('user:{}:avgsize'.format(userid), (float(avgsize) * (float(cnttxt) + diff) + size) / float(cnttxt))
	else:
		r.set('user:{}:avgsize'.format(userid), size)

def update_user_average_polarity(userid, polarity, diff=-1):
	avgpolarity = r.get('user:{}:avgpolarity'.format(userid))
	if avgpolarity:
		cnttxt = r.get('user:{}:cnttxt'.format(userid))
		if cnttxt:
			r.set('user:{}:avgpolarity'.format(userid), (float(avgpolarity) * (float(cnttxt) + diff) + polarity) / float(cnttxt))
	else:
		r.set('user:{}:avgpolarity'.format(userid), polarity)

def update_user_times(userid, dt):
	r.hincrby('user:{}:hours'.format(userid), dt.hour)
	r.hincrby('user:{}:days'.format(userid), dt.weekday())
	r.hincrby('user:{}:months'.format(userid), dt.month)
	r.hincrby('user:{}:years'.format(userid), dt.year)

def get_int(key):
	i = r.get(key)
	if not i:
		i = 0
	return int(i)

def get_float(key):
	f = r.get(key)
	if not f:
		f = 0
	return round(float(f), 2)

def get_int_dict(key):
	h = r.hgetall(key)
	for k in h:
		h[k] = int(h[k])
	return h

def get_hours(userid):
	hours = get_int_dict('user:{}:hours'.format(userid))
	for i in range(24):
		stri = str(i)
		if stri not in hours:
			hours[stri] = 0
	return hours

def get_months(userid):
	months = get_int_dict('user:{}:months'.format(userid))
	for i in range(1, 13):
		stri = str(i)
		if stri not in months:
			months[stri] = 0
	return months

def get_days(userid):
	days = get_int_dict('user:{}:days'.format(userid))
	for i in range(7):
		stri = str(i)
		if stri not in days:
			days[stri] = 0
	return days

def get_words(userid):
	words = get_int_dict('user:{}:words'.format(userid))
	for w in config.VALIDWORDS:
		if w not in words:
			words[w] = 0
	return words

def get_top3(key):
	dictops = {}
	listops = r.zrange(key, 0, 2, desc=True, withscores=True, score_cast_func=int)
	for t in listops:
		dictops[t[0]] = t[1]
	return dictops

def get_user(userid):
	if not r.sismember('users', userid):
		return None
		#raise
 
	user = {}
	user['id'] = userid
	user['name'] = r.get('user:{}:name'.format(userid))
	user['imgurl'] = r.get('user:{}:imgurl'.format(userid))
	user['cntmsg'] = get_int('user:{}:cntmsg'.format(userid))
	user['cnttxt'] = get_int('user:{}:cnttxt'.format(userid))
	user['cntimg'] = get_int('user:{}:cntimg'.format(userid))
	user['cntemj'] = get_int('user:{}:cntemj'.format(userid))
	user['cntstk'] = get_int('user:{}:cntstk'.format(userid))
	user['avgsize'] = get_float('user:{}:avgsize'.format(userid))
	user['avgsentiment'] = get_float('user:{}:avgpolarity'.format(userid))
	user['emojis'] = get_top3('user:{}:emojis'.format(userid))
	user['stickers'] = get_top3('user:{}:stickers'.format(userid))
	user['words'] = get_words(userid)
	user['hours'] = get_hours(userid)
	user['days'] = get_days(userid)
	user['months'] = get_months(userid)
	user['years'] = get_int_dict('user:{}:years'.format(userid))
	return user

def get_users(noglobal=True):
	userids = r.smembers('users')
	users = []
	for userid in userids:
		#try:
		if noglobal and userid == config.GLOBAL:
			continue

		users.append(get_user(userid))
		#except:
		#	pass
			#log.warn('user {} doesn\'t exists', userid)
	return users

def get_sticker(stickerid):
	if not r.sismember('stickers', stickerid):
		pass
		#raise
	sticker = {}
	sticker['id'] = stickerid
	sticker['imgurl'] = r.get('sticker:{}:imgurl'.format(stickerid))
	return sticker

def get_stickers():
	stickerids = r.smembers('stickers')
	stickers = []
	for stickerid in stickerids:
		try:
			stickers.append(get_sticker(stickerid))
		except:
			pass
			#log.warn('sticker {} doesn\'t exists', stickerid)
	return stickers


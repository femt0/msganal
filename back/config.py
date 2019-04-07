# The secret key is used by Flask to encrypt session cookies.
SECRET_KEY = 'mysecretkey'

MESSENGER_USERNAME = 'eliott.benoit@club-internet.fr'
MESSENGER_PASSWORD = '***REMOVED***'
THREAD_ID = '1312983893'

REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_APP_DB = 0
REDIS_EXCHANGE_DB = 1
REDIS_EXCHANGE_URL = 'redis://{}:{}/{}'.format(REDIS_HOST, REDIS_PORT, REDIS_EXCHANGE_DB)  

VALIDWORDS = [ 'oui', 'non', 'je', 'tu', 'moi', 'toi', 'nous', 'vous', 'tg', 'hitler', 'nazi', 'race', 'rouge', 'bleu', 'jaune', 'vert', 'orange', 'violet', 'rose', 'noir', 'blanc' ] 
GLOBAL = 'global'

DEBUG=True
#LIMIT = 20
#SCAN_RESFRESH_FREQ = 100
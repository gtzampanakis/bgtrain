import logging, os
import MySQLdb
import cherrypy as cp
import gnubg.dbapiutil as dbapiutil
import gnubg.config as c
import gnubg.gamerep as gg
from passlib.apps import custom_app_context as pwd_context

LOGGER = logging.getLogger()

def get_config_file_path():
	config_path = os.environ.get('BGTRAIN_CONFIG_FILE')
	LOGGER.info('Loaded config_path: %s', config_path)
	return config_path

def get_web_config():
	import cherrypy.lib.reprconf
	file_path = get_config_file_path()
	return cherrypy.lib.reprconf.Config(file_path)


def get_config():
	return c

def get_conn():
	import json
	import cherrypy as cp
	conn_string = get_web_config().get('db').get('conn.string')
	LOGGER.info('Loaded conn.string: %s', conn_string)
	connect_parameters = json.loads(
			os.environ.get('BGTRAIN_CONNECT_PARAMETERS')
				or
			conn_string
	)
	conn = dbapiutil.connect(
			lambda: MySQLdb.connect(**connect_parameters)
	)
	return conn

def verify_password(password_provided, password_hash):
	result = pwd_context.verify(password_provided, password_hash)
	return result

def get_password_hash(password):
	result = pwd_context.encrypt(password)
	return result

def check_username_password(username, password):
	if c.DEBUG:
		return True
	sql = 'select pwhash, username from users where username = %s and pwhash is not null'
	row = cp.thread_data.conn.execute(sql, [username]).fetchone()
	if row:
		password_hash = row[0]
		username = row[1] # To get the normalized case
		if verify_password(password, password_hash):
			return True
	return False

def normalize_limits(current_i, context_i, max_i):
	low_limit = max([1, current_i - context_i])
	high_limit = min([current_i + context_i + 1, max_i + 1])
	total_i = context_i * 2 + 1

	attempts = 0
	while attempts <= total_i and high_limit - low_limit < total_i:
		attempts += 1
		if low_limit != 1:
			low_limit -= 1
		if high_limit != max_i + 1:
			high_limit += 1

	return (low_limit, high_limit)

def validate_email_address(s):
	s = s.strip()
	if len(s) >= 5:
		if '@' in s:
			if '.' in s.split('@')[1]:
				return True
	return False

def should_gnuid_be_filtered(gnuid):
	return (
			gnuid.startswith('4HPwATDgc/ABMA')
			or
			gg.position_id_to_max_pips(gnuid.split(':')[0]) >= c.PIPS_THRESHOLD
	)




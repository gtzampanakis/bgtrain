import os, logging, logging.handlers, time, random
import socket, sys, platform

import platform
WINDOWS = 'Win' in platform.platform()

LOGGER = logging.getLogger(__name__)
ROOT_DIR = os.path.dirname(__file__)

class Daemon:
	""" Class that facilitates running sort-of-daemons on pythonanywhere.
	The callable f will be called every update_interval_seconds. """

	def __init__(self, logpath, update_interval_seconds, f, 
						fargs = [], fkwargs = {}, level = logging.INFO,
						also_log_to_stderr = False):
		self.logpath = logpath
		self.update_interval_seconds = update_interval_seconds
		self.level = level
		self.also_log_to_stderr = also_log_to_stderr
		self.f = f
		self.fargs = fargs
		self.fkwargs = fkwargs

	def start(self):
		root_logger = logging.getLogger()
		formatter = logging.Formatter(fmt = '%(asctime)s %(levelname)s %(name)s: %(message)s')
		root_logger.setLevel(self.level)
		if self.also_log_to_stderr:
			stream_handler = logging.StreamHandler()
			stream_handler.setFormatter(formatter)
			stream_handler.setLevel(self.level)
		rotating_file_handler = logging.handlers.RotatingFileHandler(
				self.logpath,
				maxBytes = 10 * 1024 * 1024, 
				backupCount = 3, 
				encoding = 'utf-8'
		)
		rotating_file_handler.setFormatter(formatter)
		rotating_file_handler.setLevel(self.level)
		if self.also_log_to_stderr:
			root_logger.addHandler(stream_handler)
		root_logger.addHandler(rotating_file_handler)

		try:
			if WINDOWS:
				lock_socket = socket.socket()
			else:
				lock_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
			try:
				if WINDOWS:
					port_to_use = random.randint(30000, 63000)
					LOGGER.info('Binding to port %s', port_to_use)
					lock_socket.bind(('localhost', port_to_use))
				else:
					lock_id = str('gtzampanakis')
					lock_socket.bind('\0' + lock_id)
				LOGGER.debug('Successfully acquired lock')
				while True:
					t0 = time.time()
					self.f(*self.fargs, **self.fkwargs)
					t1 = time.time()
					time_taken = t1 - t0
					to_wait = self.update_interval_seconds - time_taken
					if to_wait < 0.:
						to_wait = 0
					time.sleep(to_wait)
			except socket.error:
				print 'Failed to acquire lock'
				LOGGER.debug('Failed to acquire lock')
				return

		except Exception as exc:
			LOGGER.exception(exc)
			raise

if __name__ == '__main__':
	def f(): print 1

	daemon = Daemon(
			logpath = os.path.join('test.log'),
			update_interval_seconds = 1,
			f = f,
			level = logging.DEBUG,
			also_log_to_stderr = 1)

	daemon.start()


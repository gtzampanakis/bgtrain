import os, unittest, threading
import wsgiref.validate
import wsgiref.simple_server
import cherrypy, urllib
import gnubg
import gnubg.webapp as gw
import gnubg.common as gc

ROOT_DIR = os.path.dirname(__file__)

SERVER_HOST = 'localhost'
SERVER_PORT = 8080
SERVER_URL = 'http://' + SERVER_HOST + ':' + str(SERVER_PORT)

class EnvironmentTests(unittest.TestCase):

	def get_cherrypy_config_path(self):
		return gc.get_config_file_path()

	def get_parsed_cherrypy_config(self):
		return gc.get_web_config()



	def setUp(self):
		pass




	def test_import_webapp(self):
		import gnubg.webapp

	def test_gnubg_config_exists(self):
		gc.get_config()

	def test_cherrypy_config_exists(self):
		self.assertTrue(os.path.exists(self.get_cherrypy_config_path()))

	def test_cherrypy_config_valid(self):
		self.get_parsed_cherrypy_config()

	def test_db_access(self):
		gc.get_conn()




	def tearDown(self):
		pass


class PasswordTests(unittest.TestCase):

	def test_correct_password(self):
		password = 'abcdefghijklmnopqrstuvwxyz 0123456789'
		hash_ = gc.get_password_hash(password)
		self.assertTrue(gc.verify_password(password, hash_))

	def test_incorrect_password(self):
		password = 'abcdefghijklmnopqrstuvwxyz 0123456789'
		hash_ = gc.get_password_hash(password)
		hash_to_send = gc.get_password_hash(password + 'a')
		self.assertFalse(gc.verify_password(password, hash_to_send))

	def test_valid_email_address(self):
		email = 'giorgos@foo.com'
		self.assertTrue(gc.validate_email_address(email))

	def test_valid_email_address(self):
		email = 'giorgosfoo.com'
		self.assertFalse(gc.validate_email_address(email))


class WebAppTests(unittest.TestCase):

	done_serving = False

	def serve(self):
		while True:
			if self.done_serving:
				break
			self.server.handle_request()

	def setUp(self):
		app = gw.Application()
		app = cherrypy.Application(app, '', config = gc.get_config_file_path())
		app = wsgiref.validate.validator(app)
		self.server = wsgiref.simple_server.make_server(
										SERVER_HOST, SERVER_PORT, app)
		self.server_thread = threading.Thread(target = self.serve)
		self.server_thread.start()

	def test_access(self):
		pass

	def tearDown(self):
		self.done_serving = True
# Following call is just to make self.server.handle_request() return and thus
# make the serve() function check the done_serving flag and exit.
		urllib.urlopen(SERVER_URL)



if __name__ == '__main__':
	unittest.main()
		


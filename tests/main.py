import os, unittest
import cherrypy
import gnubg
import gnubg.common as gc

ROOT_DIR = os.path.dirname(__file__)


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


if __name__ == '__main__':
	unittest.main()
		


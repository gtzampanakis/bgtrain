import os, unittest, threading, subprocess, json, tempfile, os
import wsgiref.validate
import wsgiref.simple_server
import cherrypy, urllib.request, urllib.parse, urllib.error, requests
import gnubg
import webapp as gw
import common as gc

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

def get_launched_mysql_process():
    db_parameters = json.loads(gc.get_web_config()['db']['conn.string'])

    process = subprocess.Popen(
            [
                'mysql',
                '--user=' + db_parameters['user'],
                '--password=' + db_parameters['passwd'],
                '--force',
            ],
            stdin = subprocess.PIPE,
    )

    return process

class WebAppTests(unittest.TestCase):

    DB_NAME = 'BGTRAIN_UNITTEST'
    done_serving = False

    @classmethod
    def setUpClass(cls):
        schema_file_path = os.path.join(os.path.dirname(gnubg.__file__), 
                                                'db_schema', 'db_schema.sql')

        process = get_launched_mysql_process()

        process.stdin.write('DROP DATABASE ' + cls.DB_NAME + ';\n')
        process.stdin.write('CREATE DATABASE ' + cls.DB_NAME + ';\n')
        process.stdin.write('USE ' + cls.DB_NAME + ';')
        with open(schema_file_path) as schema_file:
            while True:
                to_write = schema_file.read(1024)
                if not to_write:
                    break
                process.stdin.write(to_write)

        process.stdin.close()
        process.wait()

        web_config = gc.get_web_config()
        db_parameters = json.loads(web_config['db']['conn.string'])
        db_parameters['db'] = cls.DB_NAME
        web_config['db']['conn.string'] = json.dumps(db_parameters)
        os.environ['BGTRAIN_CONNECT_PARAMETERS'] = json.dumps(db_parameters)

        app = gw.Application()
        app = cherrypy.Application(app, '', config = gc.get_config_file_path())
        app = wsgiref.validate.validator(app)
        server = wsgiref.simple_server.make_server(
                                        SERVER_HOST, SERVER_PORT, app)

        def serve():
            while True:
                if cls.done_serving:
                    break
                server.handle_request()

        cls.server_thread = threading.Thread(target = serve)
        cls.server_thread.start()

    def test_access(self):
        out = requests.get(SERVER_URL)
        self.assertEqual(out.status_code, 200)

    def test_registration_matching_passwords(self):
        username = '__test123__'
        password = '__test123__'
        out = requests.post(SERVER_URL + '/register', data = {
            'username' : username,
            'password' : password,
            'password_again' : password,
        })
        self.assertEqual(out.status_code, 200)
        with gc.get_conn() as conn:
            users_found = conn.execute('''
                select count(*)
                from users
                where username = %s
            ''', [username]).fetchone()[0]
            self.assertEqual(users_found, 1)

    def test_registration_nonmatching_passwords(self):
        username = '__test123__'
        password = '__test123__'
        out = requests.post(SERVER_URL + '/register', data = {
            'username' : username,
            'password' : password,
            'password_again' : password + ' ',
        })
        self.assertNotEqual(out.status_code, 200)

    @classmethod
    def tearDownClass(cls):
        cls.done_serving = True
# A request to cause the done_serving value to be read.
        requests.get(SERVER_URL)

        process = get_launched_mysql_process()
        process.stdin.write('DROP DATABASE ' + cls.DB_NAME + ';\n')
        process.stdin.close()
        process.wait()



if __name__ == '__main__':
    unittest.main()
        


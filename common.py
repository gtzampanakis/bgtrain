import logging, os
import sqlite3
import cherrypy as cp
import dbapiutil
import config as c
import gamerep as gg
from passlib.apps import custom_app_context as pwd_context

LOGGER = logging.getLogger()

CHEQUER_DECISION = 'Q'
DOUBLE_OR_ROLL_DECISION = 'D'
TAKE_OR_DROP_DECISION = 'T'

SQLITE3_CONN_STRING_PREFIX = 'sqlite3://'

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
    conn_string = get_web_config().get('db').get('conn_string')
    assert conn_string.startswith(SQLITE3_CONN_STRING_PREFIX)
    path = conn_string[len(SQLITE3_CONN_STRING_PREFIX):]
    conn = dbapiutil.connect(
        dbapi_module = sqlite3,
        connect_args = [path],
        connect_kwargs = dict(isolation_level=None),
        init_statements = ['PRAGMA foreign_keys = ON'],
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

def is_bearoff(matchid):
    points = gg.position_id_to_points(matchid)[25:]
    if sum(points[6:]) == 0:
        return True

def is_bearoffopp(matchid):
    points = gg.position_id_to_points(matchid)[:25]
    if sum(points[6:]) == 0:
        return True

def points_to_most_backward(points):
    for pointi in  range(24, -1, -1):
        if points[pointi] != 0:
            return pointi

def is_nocontact_strict(matchid):
    points = gg.position_id_to_points(matchid)
    player1points = points[25:]
    player2points = points[:25]
    player1mostbackward = points_to_most_backward(player1points)
    player2mostbackward = points_to_most_backward(player2points)
    if player1mostbackward + player2mostbackward <= 22:
        return True


def is_nocontact(matchid):
    if is_bearoff(matchid) or is_bearoffopp(matchid):
        return False
    return is_nocontact_strict(matchid)

def should_gnuid_be_filtered(gnuid, decision_type):
    return (
            gnuid.startswith('4HPwATDgc/ABMA')
                or
# Maybe we should keep cases where the roll does not allow both checkers to be
# taken off, but I really don't think it is worth the effort.
            ( decision_type == CHEQUER_DECISION and is_bearoff(gnuid) and is_nocontact_strict(gnuid) )
                or
            gg.position_id_to_max_pips(gnuid.split(':')[0]) >= c.PIPS_THRESHOLD
    )




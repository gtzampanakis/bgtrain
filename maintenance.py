import logging, os, itertools
import common as gc
from daemon import Daemon

logger = logging.getLogger(__name__)
ROOT_DIR = os.path.dirname(__file__)

def main():
    with gc.get_conn() as conn:
        conn.execute('''
            update stats
            set numofpositions = (
                select count(*)
                from posmatchids p1
                where p1.version >= %s
            )
            ,numofsubmissionslast24h = (
                select count(*)
                from usersposmatchids
                where submittedat > datetime('now', '-1 day')
            )
            ''',
            [gc.get_config().POSITIONS_VERSION_TO_USE]
        )
            
if __name__ == '__main__':
    ALSO_TO_STDERR = 0
        
    daemon = Daemon(
            logpath = os.path.join(ROOT_DIR, 
                os.path.basename(os.path.abspath(__file__)) + '.log'),
            update_interval_seconds = 5 * 60,
            f = main,
            also_log_to_stderr = ALSO_TO_STDERR,
            level = logging.DEBUG,
    )

    daemon.start()




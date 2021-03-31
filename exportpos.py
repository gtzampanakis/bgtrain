import logging, os, itertools
import common as gc

logger = logging.getLogger(__name__)
ROOT_DIR = os.path.dirname(__file__)

def export():
    with gc.get_conn() as conn:
        rs = conn.execute('''
            select 
            pm.posmatchid,
            pm.decisiontype,
            an.move,
            an.equity,
            pm.version,
            an.ply

            from 

            posmatchids pm
            join analyses an on pm.posmatchid = an.posmatchid

            where coalesce(pm.exported, 0) = 0

            order by 
            
            pm.posmatchid,
            an.equity desc
        ''')

        for suffint in itertools.count(1):
            path = os.path.join(
                    ROOT_DIR,
                    'dump',
                    str(suffint) + '.csv',
            )
            if not os.path.exists(path):
                break
        exported = [ ]
        with open(path, 'wb') as outf:
            for row in rs:
                posmatchid, decisiontype, move, equity, version, ply = row
                outf.write(';'.join(str(c) for c in row))
                outf.write('\n')
                exported.append(posmatchid)

        for posmatchid in exported:
            conn.execute('''
            update posmatchids
            set exported = 1
            where posmatchid = %s
            ''', [posmatchid])
            
if __name__ == '__main__':
    export()


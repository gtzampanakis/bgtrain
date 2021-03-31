import logging, os, sys
import common as gc
import gamerep as gamerep

LOGGER = logging.getLogger(__name__)

def is_opening(matchid):
    pips_pair = gamerep.position_id_to_pips(matchid)
    if all(pips > 145 for pips in pips_pair):
        return True

def is_closing(matchid):
    pips_pair = gamerep.position_id_to_pips(matchid)
    if all(pips < 70 for pips in pips_pair):
        return True

def is_midgame(matchid):
    pips_pair = gamerep.position_id_to_pips(matchid)
    if all(100 < pips < 120 for pips in pips_pair):
        return True


def is_backgame(matchid):
    if gc.is_nocontact(matchid):
        return False
    points = gamerep.position_id_to_points(matchid)[25:]
    opp_pips, player_pips = gamerep.position_id_to_pips(matchid)
    board = points[-7:-1]
    if (sum(1 for point in board if point >= 2) >= 2
                            and player_pips - opp_pips >= 55):
        return True

def is_backgameopp(matchid):
    if gc.is_nocontact(matchid):
        return False
    points = gamerep.position_id_to_points(matchid)[:25]
    opp_pips, player_pips = gamerep.position_id_to_pips(matchid)
    board = points[-7:-1]
    if (sum(1 for point in board if point >= 2) >= 2
                            and opp_pips - player_pips >= 55):
        return True

def is_holding(matchid):
    if gc.is_nocontact(matchid):
        return False
    points = gamerep.position_id_to_points(matchid)[25:]
    opp_pips, player_pips = gamerep.position_id_to_pips(matchid)
    board = points[-8:-3]
    if (sum(1 for point in board if point >= 2) == 1
                            and player_pips - opp_pips >= 55):
        return True

def is_holdingopp(matchid):
    if gc.is_nocontact(matchid):
        return False
    points = gamerep.position_id_to_points(matchid)[:25]
    opp_pips, player_pips = gamerep.position_id_to_pips(matchid)
    board = points[-8:-3]
    if (sum(1 for point in board if point >= 2) == 1
                            and opp_pips - player_pips >= 55):
        return True



if __name__ == '__main__':
    with gc.get_conn() as conn:

        def add_tag(matchid, tag):
            print('Called add_tag with %s and %s' % (matchid, tag))
            insert_tag_sql = '''
                insert into postags
                (posmatchid, tag, createdat)
                values
                (%s, %s, current_timestamp)
            '''
            conn.execute(insert_tag_sql, [matchid, tag])

        TAG_SQL = '''
            select tag, donetagging
            from tags
            order by tag
        '''

        tags_to_process = [
                tag
                for tag, donetagging
                in conn.execute(TAG_SQL)
                if donetagging != '1'
        ]

        if len(tags_to_process) == 0:
            sys.exit()

        SQL = '''
            select
            posmatchid
            from posmatchids
            where 1=1
        '''

        rs = conn.execute(SQL)
        for rowi, row in enumerate(rs):
            posmatchid = row[0]
            for tag in tags_to_process:
                func = globals()['is_' + tag]
                if func(posmatchid):
                    add_tag(posmatchid, tag)
            if rowi % 500 == 0:
                print(rowi)
                conn.commit()
        conn.execute('update tags set donetagging = 1')


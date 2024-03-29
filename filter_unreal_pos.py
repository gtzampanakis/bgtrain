import gamerep as gg
import common as gc

def find_threshold():
    with gc.get_conn() as conn:
        gnuids = conn.execute('select posmatchid from posmatchids')
        gnuids = (row[0] for row in gnuids)
        m = [(gnuid, gg.position_id_to_max_pips(gnuid.split(':')[0])) for gnuid in gnuids]
        m.sort(key = lambda o: o[1])
        total_records = len(m)
        print(m[int(total_records * .95)])

def main():
    with gc.get_conn() as conn:
        it = conn.execute('select posmatchid, decisiontype from posmatchids')
        for row in it:
            gnuid = row[0]
            decision_type = row[1]
            if gc.should_gnuid_be_filtered(gnuid, decision_type):
                print('Deleting gnuid:', gnuid)
                conn.execute('delete from posmatchids where posmatchid = %s', [gnuid])
                conn.commit()

if __name__ == '__main__':
    main()

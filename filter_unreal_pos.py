import gnubg.gamerep as gg
import gnubg.common as gc

def find_threshold():
	with gc.get_conn() as conn:
		gnuids = conn.execute('select posmatchid from posmatchids')
		gnuids = (row[0] for row in gnuids)
		m = [(gnuid, gg.position_id_to_max_pips(gnuid.split(':')[0])) for gnuid in gnuids]
		m.sort(key = lambda o: o[1])
		total_records = len(m)
		print m[int(total_records * .95)]

def main():
	with gc.get_conn() as conn:
		posmatchid_iter = conn.execute('select posmatchid from posmatchids')
		for row in posmatchid_iter:
			gnuid = row[0]
			if gc.should_gnuid_be_filtered(gnuid):
				print 'Deleting gnuid:', gnuid
				conn.execute('delete from posmatchids where posmatchid = %s', [gnuid])
				conn.commit()

if __name__ == '__main__':
	main()

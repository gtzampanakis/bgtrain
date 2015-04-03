import logging, os
import gnubg.common as gc
import gnubg.gamerep as gamerep

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

FUNC_TO_TAG = {
		is_opening: 'opening',
		is_closing: 'closing',
		is_midgame: 'midgame',
}


if __name__ == '__main__':
	with gc.get_conn() as conn:

		def add_tag(matchid, tag):
			print 'Called add_tag with %s and %s' % (matchid, tag)
			insert_tag_sql = '''
				insert into postags
				(posmatchid, tag, createdat)
				values
				(%s, %s, utc_timestamp())
			'''
			conn.execute(insert_tag_sql, [matchid, tag])

		SQL = '''
			select
			posmatchid
			from posmatchids
			where 1=1
			and (tagged <> 1 or tagged is null)
		'''

		rs = conn.execute(SQL)
		for rowi, row in enumerate(rs):
			posmatchid = row[0]
			for func, tag in FUNC_TO_TAG.iteritems():
				if func(posmatchid):
					add_tag(posmatchid, tag)
			conn.execute('update posmatchids set tagged = 1 where posmatchid = %s', 
																		[posmatchid])
			if rowi % 200 == 0:
				print rowi
				conn.commit()


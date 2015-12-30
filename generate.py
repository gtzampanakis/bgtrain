import logging, os, uuid, re, glob, sqlite3, shutil, itertools, time, datetime, copy
import gamerep
import subprocess as sp
import gnubg.common as gc

logger = logging.getLogger(__name__)

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


GNUBG_PATH = gc.get_web_config().get('gnubg').get('program_path')
COMMANDS_PATH = gc.get_web_config().get('gnubg').get('commands_path')
SAVE_PATH = os.path.join(ROOT_DIR, 'matches')
WORK_SUFFIX = '.work'

TEXT_BUFFER_SIZE = 200

def scan(pairs, text, *args):
	start = 0
	while True:
		mo = None
		for matcher, handler in pairs:
			mo = matcher.match(buffer(text, start, TEXT_BUFFER_SIZE))
			if mo:
				start += mo.end()
				if handler:
					handler(mo, *args)
				break
		if start >= len(text):
			break
		if not mo:
			start += 1
			

def position_id_handler(mo, *args):
	global analyzed
	analyzed = Analyzed()
	analyzed.position_id = mo.group(1)

def match_id_handler(mo, *args):
	analyzed.match_id = mo.group(1)
	
def move_handler(mo, *args):
	analyzed.move = mo.group('MOVE')
	analyzed.equity = float(mo.group('EQ').replace(',', '.'))

	if 'double' in mo.group().lower():
		if gamerep.is_cube_being_offered(analyzed.match_id):
			analyzed.type = gc.TAKE_OR_DROP_DECISION
		else:
			analyzed.type = gc.DOUBLE_OR_ROLL_DECISION
	else:
		analyzed.type = gc.CHEQUER_DECISION

	if analyzed.type == gc.CHEQUER_DECISION:
		analyzed.ply = int(mo.group('PLY'))

	store(analyzed)

def cannot_move_handler(mo, *args):
	global analyzed
	analyzed = None

def cube_ply_handler(mo, *args):
	analyzed.ply = int(mo.group('PLY'))

position_id_re = r'GNU Backgammon\s+Position ID: (?P<PID>\S+)'
match_id_re = r'Match ID\s*: (?P<MID>\S+)'
cannot_move_re = r'Cannot move'
chequer_analysis_re = r'[\*\s]*\d+\.\s*Cube(ful|less)\s+(?P<PLY>\d+)-ply\s+(?P<MOVE>.+?)\s+Eq\.:\s+(?P<EQ>[+-][\d,\.]+)'
chequer_analysis_re = r'Cube(ful|less)\s+(?P<PLY>\d+)-ply\s+(?P<MOVE>.+?)\s+Eq\.:\s+(?P<EQ>[+-][\d,\.]+)'
cube_analysis_re = r'\d+\. (?P<MOVE>No double|Double, pass|Double, take)\s+(?P<EQ>[+-][\d,\.]+)'
cube_ply_re = r'(?P<PLY>\d+)-ply cubeless equity'

pairs = ([
	[re.compile(position_id_re			), 		position_id_handler],
	[re.compile(match_id_re				), 		match_id_handler],
	[re.compile(cube_ply_re				), 		cube_ply_handler],
	[re.compile(cube_analysis_re		), 		move_handler],
	[re.compile(cannot_move_re			), 		cannot_move_handler],
	[re.compile(chequer_analysis_re		), 		move_handler],
])
			

def scan_not_proper(pairs, text, *args):
	start = 0
	hit_found = None
	while hit_found is None or hit_found:
		hit_found = False
		for matcher, handler in pairs:
			while True:
				mo = matcher.search(text[start:])
				if mo:
					hit_found = True
					start += mo.end()
					if handler:
						handler(mo, *args)
				else:
					break

class Analyzed:
	pass

stored = [ ]
def store(analyzed):
	if gamerep.whose_turn(analyzed.match_id) == gamerep.BLACK_PLAYER:
# Delete is not needed since we store all possible moves, and those will be the
# same no matter what the configuration of GNUBG.
		match_id = (analyzed.match_id
				if analyzed.type != gc.DOUBLE_OR_ROLL_DECISION
				else gamerep.set_dice_to_zero(analyzed.match_id))
		posmatchid = analyzed.position_id + ':' + match_id
		if not gc.should_gnuid_be_filtered(posmatchid, decision_type):
			analyzed.posmatchid = posmatchid
			stored.append(copy.copy(analyzed))

def std(x):
	from math import sqrt 
	n, mean, std = len(x), 0, 0 
	for a in x: 
		mean = mean + a 
	mean = mean / float(n) 
	for a in x: 
		std = std + (a - mean)**2
	std = sqrt(std / float(n-1)) 
	return std

def write_to_csv():
	global stored
	for posmatchid, group in itertools.groupby(stored, lambda an: an.posmatchid):
		group = list(group)
		group_for_std = [ ]
		for analyzed in group:
			if (
					analyzed.type == 'Q'
					or
					analyzed.type == 'T' and analyzed.move.startswith('Double,')
					or
					analyzed.type == 'D' and (
						analyzed.move == 'No double' 
						or 
						analyzed.move.startswith('Double') and
						len([
							1 for gi in group
							if gi.move.startswith('Double') and gi.equity < analyzed.equity
						]) == 0
					)
				):
					group_for_std.append(analyzed)
		if len(group) > 1 and std([gi.equity for gi in group_for_std]) > gc.get_config().STD_THRESHOLD:
			for analyzed in group:
				row = [posmatchid, analyzed.type, analyzed.move, 
						analyzed.equity, args.version, analyzed.ply]
				OUTPUT_FILE.write(';'.join(str(c) for c in row))
				OUTPUT_FILE.write('\n')
	stored = [ ]



if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument('minutes', help = 'Number of minutes to work for', type = float)
	parser.add_argument('version', help = 'Analysis version to store', type = int)
	args = parser.parse_args()
	if 1:
		with open(COMMANDS_PATH, 'r') as commands_file:
			gnubg_config = commands_file.read()
		start_time = time.time()
		while True:
			process = sp.Popen(
					[
						GNUBG_PATH,
						'-q',
						'-r',
						'-t',
					],
					stdin = sp.PIPE,
			)
			process.stdin.write(gnubg_config)
			process.stdin.write('new match\n')
			process.stdin.write('analyse match\n')
			batch_id = uuid.uuid4()
			filename = str(batch_id)
			process.stdin.write('save match ' + os.path.join(SAVE_PATH, filename + '.sgf') + '\n')
			process.stdin.write('export match text ' + os.path.join(SAVE_PATH, filename) + '.an.txt\n')
			process.stdin.write('quit\n')
			return_code = process.wait()
			if return_code != 0:
				raise Exception('Abnormal GNUBG termination')

			for analysis_filename in glob.glob(os.path.join(SAVE_PATH, filename + '*txt')):
				with open(analysis_filename, 'r') as analysis_file:
					analysis_text = buffer(analysis_file.read())
					scan(pairs, analysis_text)
					print '--------------------------------'
					OUTPUT_PATH = datetime.datetime.strftime(
							datetime.datetime.now(), 
							'exportpos_%Y-%m-%dT%H.%M.%S.%f.csv'
					)
					WORK_PATH = os.path.join(ROOT_DIR, 'dump', OUTPUT_PATH + WORK_SUFFIX)
					print 'Writing', WORK_PATH, '...'
					with open(WORK_PATH, 'wb') as OUTPUT_FILE:
						write_to_csv()
					print 'Done writing', WORK_PATH, '.'
					os.rename(WORK_PATH, WORK_PATH[: -len(WORK_SUFFIX)])
				dest_path = os.path.join(SAVE_PATH, 'processed', os.path.basename(analysis_filename))
				shutil.move(analysis_filename, dest_path)
			if (time.time() - start_time) / 60. > args.minutes:
				break


import re, itertools
from pprint import pprint as pp

WHITE_PLAYER = 0
BLACK_PLAYER = 1
BAR_INDEX = 24

move_re = re.compile(r'([BW])\[(?:\d{2})?([a-z]{0,8}|double|take|drop)\]')

game_re = re.compile(r'''
 \(;FF\[(?P<SGFVERSION>\d+)\]
 GM\[6\] 		# GM[6] means that the game recorded is backgammon
 CA\[UTF-8\]
 AP\[(?P<GNUBGVERSION>.*?)\]
 MI(?:\[.+?:.+?\])+?
 \[ws:(?P<WHITESCORE>\d+)\]
 \[bs:(?P<BLACKSCORE>\d+)\]
 PW\[.*?\]
 PB\[.*?\]
 (DT\[.*?\])?
 RU\[.*?\]
 RE\[.*?\]
 .*?
 \s*
# Moves:
 (?P<MOVES>(?:;[BW].*?\s*)*)
# End of moves.
 \)
''', re.VERBOSE)

turn_re = re.compile(r'''
 ;(?P<TURNANDMOVE>
 	(?P<PTURN>[BW])
	 \[(?P<MOVE>\d{2}([a-z]{2}){0,4}|double|take|drop)\]
 )
 (DA\[(?P<CUBEANALYSIS>.*?)\])?
 (A\[0\](?P<CHEQANALYSIS>(\[.*?\])*))?
''', re.VERBOSE)

def iter_over_moves(path):
	with open(path, 'rb') as fo:
		text = fo.read()
	for game_mo in game_re.finditer(text):
		moves_str = game_mo.group('MOVES')
		yield game_mo, turn_re.finditer(moves_str)
		#for turn_mo in turn_re.finditer(moves_str):
		#	#yield gamei, turn_mo.group('TURNANDMOVE')
		#	yield gamei, turn_mo

class GameFinishedException(Exception):
	pass


def letter2index(letter, player):
	if player == BLACK_PLAYER:
		return ord(letter) - ord('a')
	elif player == WHITE_PLAYER:
		return ord('x') - ord(letter)
	else:
		raise Exception

def index2letter(index, player):
	if player == BLACK_PLAYER:
		return ('abcdefghijklmnopqrstuvwx' + 'yz')[index]
	elif player == WHITE_PLAYER:
		return (list(reversed('abcdefghijklmnopqrstuvwx')) + ['y', 'z'])[index]
	else:
		raise Exception

class GameState:
	def __init__(self):
		self.cheq_distr = [[0] * 25, [0] * 25]
		for player in [WHITE_PLAYER, BLACK_PLAYER]:
			self.cheq_distr[player][1-1] = 2
			self.cheq_distr[player][12-1] = 5
			self.cheq_distr[player][17-1] = 3
			self.cheq_distr[player][19-1] = 5
		self.cube = 1
		self.won = None

	def do_sgf_move(self, sgf_move):
		""" "move" is in sgf format. """
		if self.won is not None:
			raise GameFinishedException
		mo = move_re.match(sgf_move)
		provided_move_made_by = WHITE_PLAYER if mo.group(1) == 'W' else BLACK_PLAYER
		sign = -(1 if provided_move_made_by == WHITE_PLAYER else -1)
		move = mo.group(2)
		if move == 'take':
			self.cube *= 2
		elif move == 'double':
			pass
		elif move == 'drop':
			self.won = sign * 1
		else:
			assert len(move) % 2 == 0
			for start in xrange(0, len(move), 2):
				pair = move[start:start+2]
				a, b = pair
# Black player goes forward in the alphabet, white player goes backward.
				if b == 'z':
					if a in 'stuvwx':
						move_made_by = BLACK_PLAYER
					else:
						move_made_by = WHITE_PLAYER
				elif a == 'y':
					if b in 'abcdef':
						move_made_by = BLACK_PLAYER
					else:
						move_made_by = WHITE_PLAYER
				else:
					if a < b:
						move_made_by = BLACK_PLAYER
					else:
						move_made_by = WHITE_PLAYER
				assert move_made_by == provided_move_made_by
				self.cheq_distr[move_made_by][letter2index(a, move_made_by)] -= 1
				if b != 'z':
					self.cheq_distr[move_made_by][letter2index(b, move_made_by)] += 1
					if self.cheq_distr[1-move_made_by][letter2index(b, 1-move_made_by)] == 1:
# There was a hit.
						self.cheq_distr[1-move_made_by][letter2index(b, 1-move_made_by)] = 0
						self.cheq_distr[1-move_made_by][BAR_INDEX] += 1
				if sum(self.cheq_distr[move_made_by]) == 0:
					sign = 1 if move_made_by == WHITE_PLAYER else -1
					if sum(self.cheq_distr[1-move_made_by]) == 15:
						if sum(self.cheq_distr[1-move_made_by][:6]) > 0:
							self.won = sign * 3
						else:
							self.won = sign * 2
					else:
						self.won = sign * 1
		assert all(n >= 0 for n in self.cheq_distr[0])
		assert all(n >= 0 for n in self.cheq_distr[1])

class MatchState:

	def __init__(self):
		self.score = [0, 0]

	def from_sgf(self, path):
		for game_mo, turn_mo_iter in iter_over_moves(test_path):
			gs = GameState()
			print game_mo.group('WHITESCORE'), game_mo.group('BLACKSCORE')
			for turn_mo in turn_mo_iter:
				turn_and_move = turn_mo.group('TURNANDMOVE')
				cube_analysis = turn_mo.group('CUBEANALYSIS')
				cheq_analysis = turn_mo.group('CHEQANALYSIS')
				gs.do_sgf_move(turn_and_move)
				if cube_analysis is not None:
					cube_analysis_split = cube_analysis.split()
					pp(cube_analysis_split)
				#pp(gs.cheq_distr)
# For the time being we're not interested in who won, as we will only use the analysis.
			#if gs.won is not None:
			#	self.score[WHITE_PLAYER if gs.won > 0 else BLACK_PLAYER] += abs(gs.won) * gs.cube
			#else:
			#	pass
					
		

if __name__ == '__main__':
	test_path = r'matches\f82e686a-f74a-4353-a7aa-8d5f92da88a5.sgf'
	if 0:
		ms = GameState()
		print ms.cheq_distr
		ms.do_sgf_move('B[15stlq]')
		print ms.cheq_distr
		ms.do_sgf_move('W[23mkxu]')
		print ms.cheq_distr
	elif 0:
		ms = GameState()
		for gamei, move in list(iter_over_moves(test_path))[:1000]:
			print 'New turn in game: ' + str(gamei)
			print ' ',
			for letter in reversed('abcdefghijklmnopqrstuvwx'):
				print letter, '',
			print
			pp(ms.cheq_distr)
			print ' ',
			for letter in 'abcdefghijklmnopqrstuvwxyz':
				print letter, '',
			print
			pp(move)
			ms.do_sgf_move(move)
			pp(ms.won)
	elif 1:
		ms = MatchState()
		ms.from_sgf(test_path)

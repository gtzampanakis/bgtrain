import logging, os, urllib, random, numpy, collections, itertools, time
import cherrypy as cp
import mako.template as mt
import mako.lookup as ml
import gnubg.webutil as webutil
import gnubg.generate as gnubggen
import gnubg.common as gc
import gnubg.config as conf
import gnubg.elo as elo

logger = logging.getLogger(__name__)

ROOT_DIR = os.path.dirname(__file__)
ENCODING = 'utf-8'

DEFAULT_PLAYER_RATING = 1500.
DEFAULT_POSITION_RATING = 1650.

lookup = ml.TemplateLookup(directories = [
	ROOT_DIR,
])

DEFAULT_PREFERENCES = dict(
		plr_checker = 'white_checker.png',
		oppt_checker = 'red_checker.png',
)

def get_preferences():

	username = get_username_to_use()

	sql = """
		select name, value
		from preferences
		where username = %s
	"""

	rs = cp.thread_data.conn.execute(sql, [username])

	d = dict(DEFAULT_PREFERENCES)
	d.update(rs)
	return d

AVAILABLE_TAGS = [
	'opening', 'closing', 'midgame', 'bearoff', 'bearoffopp',
	'backgame', 'backgameopp', 'holding', 'holdingopp',
	'nocontact',
]


def html(f):
	def f_(self, *args, **kwargs):
		cp.response.headers['content-type'] = 'text/html;charset=' + ENCODING
		return f(self, *args, **kwargs)
	return f_

def get_info_for_position(posmatchid, for_update = False):
	sql = '''
		select rating, submissions
		from posmatchids
		where posmatchid = %s
		{for_update}
	'''.format(for_update = 'for update' if for_update else '')
	row = cp.thread_data.conn.execute(sql, [posmatchid]).fetchone()
	if row:
		return (row[0], (row[1] or DEFAULT_POSITION_RATING))


def get_user_info_for_username(username, for_update = False):
	sql = """
		select rating, submissions
		from users
		where username = %s
		{for_update}
	""".format(for_update = 'for update' if for_update else '')

	player_rating = DEFAULT_PLAYER_RATING
	submissions = 0

	row = cp.thread_data.conn.execute(sql, [username]).fetchone()
	if row is not None:
		player_rating = row[0]
		submissions = row[1]

	return player_rating, (submissions or 0)

def get_username_to_use_short():
	u = get_username_to_use()
	u = u if len(u) <= 25 else u[:22] + '...'
	return u


def get_number_of_positions():
	sql = """
	select numofpositions
	from stats
	"""
	return cp.thread_data.conn.execute(sql).fetchone()[0]

def get_number_of_submissions():
	sql = """
	select numofsubmissionslast24h
	from stats
	"""
	return cp.thread_data.conn.execute(sql).fetchone()[0]

def log_call(f):
	def f_(self, *args, **kwargs):
		logger.info('Starting timing of index() call')
		t0 = time.time()
		result = f(self, *args, **kwargs)
		logger.info('Time taken for index() call: %.3f', time.time() - t0)
		return result
	return f_


def get_leaderboard(offset, limit):

	sql = """
	{select}
	from users
	where submissions >= %s
	and pwhash is not null
	and lastsubmission > date_add(utc_timestamp(), interval -60 day)
	order by rating desc
	limit %s offset %s
	"""

	rs = cp.thread_data.conn.execute(
			sql.format(select = 'select username, rating, submissions'), 
			[conf.SUBMISSIONS_LIMIT_FOR_LEADERBOARD, limit, offset]
	)

	rows = [ ]
	for row in rs:
		rows.append(row)

	count = cp.thread_data.conn.execute(
			sql.format(select = 'select count(*)'),
			[conf.SUBMISSIONS_LIMIT_FOR_LEADERBOARD, 1, 0]
	).fetchone()[0]

	return dict(
			rows = rows,
			count = count,
	)

def get_user_rank(username = None):
	if username is None:
		username = get_logged_in_username()
	if username is not None:
		rows = get_leaderboard(
				0, 100 * 1000
		)['rows']
		for rowi, row in enumerate(rows, 1):
			if row[0] == username:
				return rowi
	return None
		

def authentication(f):
	def f_(self, *args, **kwargs):

		if 'username' in kwargs:
			username = kwargs.get('username')
			password = kwargs.get('password')
			success = gc.check_username_password(username, password)
			if success:
				cp.session['username'] = username
			else:
				cp.session['authentication_failure'] = True

		elif 'logout' in kwargs:
			cp.session['username'] = None
			raise cp.HTTPRedirect('/')

		else:
			# If no authentication changes have been performed then carry on:
			return f(self, *args, **kwargs)

# When a user is logged out and submits a play he is prompted to login in order
# to comment. This will ensure that in this case he is redirected to the
# position he was on:
		cp.session['pid'] = cp.session.get('pid') or cp.session.get('pid_last_submitted')

# If authentication changes have been performed then redirect to the same path,
# but this time using the GET method. This will avoid presenting the "Are you
# sure you want to resend information" dialog if a user reloads after logging
# in or out. Remember that login and logout are done via POST.
		raise cp.HTTPRedirect(cp.request.request_line.split(' ')[1])

	return f_

def ensure_logged_in(f):
	def f_(self, *args, **kwargs):
		username = get_logged_in_username()
		if username is None:
			raise cp.HTTPRedirect('/')
		return f(self, *args, **kwargs)
	return f_


def get_logged_in_username():
	return cp.session.get('username')

def get_username_to_use():
	return (get_logged_in_username() or cp.session.id)

def db(f):
	def f_(self, *args, **kwargs):
		t0 = time.time()
		with gc.get_conn() as conn:
			logger.info('Time taken for connecting to db: %.3f', time.time() - t0)
			cp.thread_data.conn = conn
			try:
				return f(self, *args, **kwargs)
			except cp.HTTPRedirect as r:
				conn.commit()
				raise
	return f_

def get_logged_in_user_email():
	sql = '''
		select 
		email
		from users
		where username = %s
	'''
	users_row = cp.thread_data.conn.execute(sql, 
						[get_logged_in_username()]).fetchone()
	return users_row[0]

	
comment = collections.namedtuple('Comment', ['id', 'usernmame', 'postedat', 'parentid', 'comment'])

def load_comments(gnuid):
	sql = '''
		select id, usernmame, postedat, parentid, comment
		from comments
		where 
		posmatchid = %s
		or
		id = %s
	'''
	tree = [ ]
	comment_id = None
	level = 0
	while True:
		rs = cp.thread_data.conn.execute(sql, [gnuid if level == 0 else None, comment_id])
		for row in rs:
			comment = Comment()
			for eli, el in enumerate(row):
				comment[eli] = el
			tree.append(comment)

def select_new_gnuid(decision_type, username_to_use, tags):

	sql_tmpl = """
	select * from (
		select pm.posmatchid
		from posmatchids pm
		where pm.decisiontype = %s
		and pm.version >= %s
		and pm.rating {comp_op} (
			select 
			u.rating
			from users u 
			where u.username = %s
		) - %s
		and {not_} exists (
			select 1 from usersposmatchids us
			where us.username = %s and us.posmatchid = pm.posmatchid
		)
		and {pos_virgin} exists (
			select 1 from usersposmatchids us2
			where us2.posmatchid = pm.posmatchid
		)
		{tagfilter}
		order by 
		pm.rating {rating_sort_dir}
		limit %s
	) sq
	order by rand()
	limit 1
	"""

	for not_ in ['not', '']:
		for tagfilter in [True, False]:
			for pos_virgin in ['', 'not']:
				for up_down in ['up', 'down']:
					tagfilter_sql = ''
					if tagfilter and tags:
						tagfilter_sql = '''
							and exists (
								select 1 from postags
								where postags.posmatchid = pm.posmatchid
								and postags.tag = '%s'
							)
						''' % tags
					sql = sql_tmpl.format(
							not_ = not_,
							comp_op = '>=' if up_down == 'up' else '<',
							rating_sort_dir = 'asc' if up_down == 'up' else 'desc',
							pos_virgin = pos_virgin,
							tagfilter = tagfilter_sql,
					)
					params = [
							decision_type,
							conf.POSITIONS_VERSION_TO_USE_FOR_AUTO_SELECTION,
							username_to_use,
							conf.RATING_DECREMENT_FOR_POS_SELECTION,
							username_to_use,
					]
					params += [
							conf.NUMBER_OF_CANDIDATES,
					]
					row = cp.thread_data.conn.execute(sql, params).fetchone()
					if row is not None:
						return row[0]
		


class ApplicationBeBackSoon:

	@cp.expose
	@html
	@webutil.template('bebacksoon.html')
	def default(self, *args, **kwargs):
		result = { }
		return result

def get_users_current_gnuid():
	sql = """
	select currentposmatchid
	from users
	where username = %s
	"""
	row = cp.thread_data.conn.execute(sql, [get_logged_in_username()])
	if row is not None:
		return row[0]


def check_if_gnuid_valid(gnuid):
	sql = """
	select 1
	from posmatchids
	where posmatchid = %s
	and version >= %s
	"""
	row = cp.thread_data.conn.execute(sql, 
			[gnuid, conf.POSITIONS_VERSION_TO_USE_FOR_AUTO_SELECTION]).fetchone()
	if row is not None:
		return True
	return False

class Application:

	@cp.expose
	@html
	@db
	@authentication
	@webutil.template('faq.html')
	def faq(self, *args, **kwargs):
		return { }

	@cp.expose
	@log_call
	@html
	@db
	@authentication
	@webutil.template('train.html')
	def index(self, *args, **kwargs):

		result = { }
		if kwargs.get('pid') is not None and check_if_gnuid_valid(kwargs.get('pid')):
			result['position_id'] = kwargs.get('pid')
		elif cp.session.get('pid') is not None and check_if_gnuid_valid(cp.session.get('pid')):
			result['position_id'] = cp.session.get('pid')
		else:

			constraint = cp.request.cookie.get('dectype')
			if constraint and constraint.value == 'checker':
				allowed = [
							gnubggen.CHEQUER_DECISION
				]
			elif constraint and constraint.value == 'cube':
				allowed = [
							gnubggen.TAKE_OR_DROP_DECISION, 
							gnubggen.DOUBLE_OR_ROLL_DECISION
				]
			else:
				allowed = [
							gnubggen.CHEQUER_DECISION,
							gnubggen.TAKE_OR_DROP_DECISION,
							gnubggen.DOUBLE_OR_ROLL_DECISION
				]

			decision_type = None
			while decision_type not in allowed:
				r = random.random()
				if r < conf.CHEQUER_DECISION_PORTION:
					decision_type = gnubggen.CHEQUER_DECISION
				elif r < conf.CHEQUER_DECISION_PORTION + conf.TAKE_OR_DROP_DECISION_PORTION:
					decision_type = gnubggen.TAKE_OR_DROP_DECISION
				else:
					decision_type = gnubggen.DOUBLE_OR_ROLL_DECISION

			conn = cp.thread_data.conn

			username_to_use = get_username_to_use()

			if get_logged_in_username() is None:
				sql = '''
					insert ignore
					into users
					(username)
					values
					(%s)
				'''
				rs = conn.execute(sql, [username_to_use])

			tags_cookie = cp.request.cookie.get('tags')
			tags = None
			if tags_cookie and tags_cookie.value in AVAILABLE_TAGS:
				tags = tags_cookie.value

			result['position_id'] = select_new_gnuid(
					decision_type, 
					username_to_use, 
					tags,
			)

		cp.session['pid'] = result['position_id']
		gnuid = result['position_id']
		virtual_submit_result = self.virtual_submit(gnuid)
		
		result.update(virtual_submit_result)

		TAGS_SQL = '''
			select tag
			from postags
			where posmatchid = %s
			order by tag
		'''
		postags = ', '.join(
			r[0] for r in
			cp.thread_data.conn.execute(TAGS_SQL, [gnuid])
		)
		result['postags'] = postags

		return result

	def virtual_submit(self, gnuid):
		"""
		Receives a gnuid and returns the output of the submit() function
		for the get_username_to_use user.
		"""
		conn = cp.thread_data.conn
		sql = '''
			select move
			from usersposmatchids
			where username = %s
			and posmatchid = %s
			order by submittedat desc
			limit 1
		'''
		row = conn.execute(sql, [get_username_to_use(), gnuid]).fetchone()
		if row is None:
			result = { }
			result['comments_html'] = get_comments_html(gnuid, False)
			return result
		else:
			move = row[0]
			submit_result = self.submit_naked(gnuid = gnuid, move = move, highlight_move = False)
			return submit_result

	@cp.expose
	@db
	@webutil.rest
	def submit(self, *args, **kwargs):
		return self.submit_naked(*args, **kwargs)

	def submit_naked(self, *args, **kwargs):
		result = { }
		highlight_move = kwargs.get('highlight_move', True)

		gnuid = kwargs.get('gnuid')
		selected_move = kwargs.get('move')

		conn = cp.thread_data.conn
		sql = """
			select move, equity, ply, posmatchids.decisiontype
			from analyses
			join posmatchids on posmatchids.posmatchid = analyses.posmatchid
			where posmatchids.posmatchid = %s
			order by
			case decisiontype when 'Q' then 1 else move end,
			ply desc,
			equity desc,
			move
		"""
		rs = conn.execute(sql, [gnuid]).fetchall()

		moves = [ ]

		decision_type = None
		current_ply = None
		current_reference_equity = None
		for row in rs:
			if row[2] != current_ply:
				current_ply = row[2]
				current_reference_equity = row[1]
			decision_type = row[3]
			assert (decision_type == gnubggen.TAKE_OR_DROP_DECISION and selected_move in ('take', 'drop')
					or
					decision_type == gnubggen.DOUBLE_OR_ROLL_DECISION and selected_move in ('double', 'roll')
					or
					decision_type == gnubggen.CHEQUER_DECISION)
			to_append = {
					'move': row[0], 
					'equity': -row[1] if decision_type == gnubggen.TAKE_OR_DROP_DECISION else row[1], 
					'ply': current_ply,
					'diff': -(rs[0][1] - row[1]),
					'diff_show': -((current_reference_equity if current_reference_equity is not None and 
												decision_type == gnubggen.CHEQUER_DECISION else rs[0][1]) - row[1]),
			}
			to_append['diff_show'] = to_append['diff_show'] if to_append['diff_show'] != 0 else None
			if row[0] == selected_move:
				to_append['highlight'] = highlight_move and True
			if not (decision_type == gnubggen.TAKE_OR_DROP_DECISION and row[0] == 'No double'):
				moves.append(to_append)

		if decision_type == gnubggen.DOUBLE_OR_ROLL_DECISION:
			equities = { }
			for row in rs:
				equities[row[0]] = row[1]

			double_equity_key = 'Double, pass' if equities['Double, pass'] < equities['Double, take'] else 'Double, take'
			ignore_key = 'Double, pass' if double_equity_key == 'Double, take' else 'Double, take'

			double_equity = equities[double_equity_key]

			best_key = double_equity_key if equities[double_equity_key] > equities['No double'] else 'No double'
			best_equity = equities[best_key]

			for move in moves:
				if move['move'] == ('No double' if selected_move == 'roll' else double_equity_key):
					move['highlight'] = highlight_move and True
				if move['move'] == ignore_key:
					move['diff'] = None
					move['disabled'] = True
				if move['move'] == best_key:
					move['diff'] = 0
				if move['move'] != ignore_key and move['move'] != best_key:
					move['diff'] = move['equity'] - best_equity

		elif decision_type == gnubggen.TAKE_OR_DROP_DECISION:
			for move in moves:
				if move['move'] == 'Double, pass':
					move['move'] = 'Drop'
				elif move['move'] == 'Double, take':
					move['move'] = 'Take'
				if move['move'].lower() == selected_move:
					move['highlight'] = highlight_move and True

			best_move = None
			best_equity = None
			for move in moves:
				if best_equity is None or move['equity'] > best_equity:
					best_equity = move['equity']
					best_move = move['move']

			for move in moves:
				if move['move'] == best_move:
					move['diff'] = 0
				else:
					move['diff'] = move['equity'] - best_equity

		if decision_type in (gnubggen.DOUBLE_OR_ROLL_DECISION, gnubggen.TAKE_OR_DROP_DECISION):
			for move in moves:
				move['diff_show'] = move['diff'] if move['diff'] != 0 else None

		else: # Checker move.
			pass

		if get_username_to_use() is not None:

			sql = """
			select 1
			from usersposmatchids
			where username = %s
			and posmatchid = %s
			limit 1
			"""

			previous_play_found = conn.execute(
					sql, 
					[get_username_to_use(), gnuid]
			).fetchone() is not None

			if not previous_play_found:

				diff = None
				selection_ply = None
				for move in moves:
					if move.get('highlight'):
						diff = move['diff']
						selection_ply = move['ply']

				if diff is not None:
					if decision_type == gnubggen.CHEQUER_DECISION and selection_ply is not None:

						min_rawequity_of_previous_ply = None
						ply_to_eq_diff = { }
						for ply, ply_rows in itertools.groupby(moves, lambda move: move['ply']):
							ply_rows = list(ply_rows)
							min_rawequity = min(r['equity'] for r in ply_rows)
							max_rawequity = max(r['equity'] for r in ply_rows)

							if min_rawequity_of_previous_ply is not None:
								eq_diff = max_rawequity - min_rawequity_of_previous_ply
								ply_to_eq_diff[ply] = eq_diff

							min_rawequity_of_previous_ply = min_rawequity

						for ply, eq_diff in ply_to_eq_diff.iteritems():
							if ply >= selection_ply:
								diff += -eq_diff -conf.PLY_PENALTY


					player_rating, player_submissions = get_user_info_for_username(
												get_username_to_use(), for_update = True)
					
					position_rating, position_submissions = get_info_for_position(
																gnuid, for_update = True)

					logger.info('equity diff: %.3f', diff)
					to_increment_player, to_increment_position = elo.match_increment(
							player_rating,
							position_rating,
							diff,
							player_submissions or 0,
							position_submissions or 0,
					)
					player_rating += to_increment_player
					position_rating -= to_increment_position

					result['player_rating'] = player_rating

# No need to return this, as it is not currently used.
					#result['position_rating'] = position_rating

					username_to_use = get_username_to_use()
					sql = '''
						insert ignore
						into users
						(username)
						values
						(%s)
					'''
					rs = conn.execute(sql, [username_to_use])

					sql = """
						insert into
						usersposmatchids
						(posmatchid, username, submittedat, move, 
						ratinguser, ratingpos, eqdiff, increment)
						values
						(%s, %s, utc_timestamp(), %s, %s, %s, %s, %s)
					"""
					params = [gnuid, get_username_to_use(), selected_move,
							player_rating, position_rating, diff, to_increment_player]
					rs = conn.execute(sql,  params)

					sql = """
						update users
						set rating = %s,
						submissions = %s,
						lastsubmission = utc_timestamp()
						where username = %s
					"""
					params = [player_rating, (player_submissions or 0) + 1, 
														get_username_to_use()]
					rs = conn.execute(sql,  params)

					sql = """
						update posmatchids
						set rating = %s,
						submissions = %s
						where posmatchid = %s
					"""
					params = [position_rating, position_submissions + 1, gnuid]
					rs = conn.execute(sql,  params)


		for move in moves:
			if 'diff' in move:
				del move['diff']
		result['moves_html'] = get_moves_html(
				moves = moves, 
				decision_type = decision_type,
		)
		result['comments_html'] = get_comments_html(
				gnuid, True
		)
		if kwargs.get('also_return_moves'):
			result['moves'] = moves
		cp.session['pid_last_submitted'] = cp.session.pop('pid')
		return result


	@cp.expose
	@html
	@db
	@authentication
	@webutil.template('playedpos.html')
	def playedpos(self, *args, **kwargs):
		result = { }

		page = int(kwargs.get('page', '1'))
		pos_list_sql = """
			select posmatchid, submittedat, 
				(select count(*) from usersposmatchids upmc where upmc.username = %s)
			from usersposmatchids upm
			where upm.username = %s
			order by submittedat desc
			limit %s offset %s
		"""

		u = kwargs.get('user') or get_username_to_use()

		pos_list_rs = cp.thread_data.conn.execute(
				pos_list_sql,
				[
					u,
					u,
					conf.POSITION_HIST_ROWS,
					conf.POSITION_HIST_ROWS * (page - 1),
				]
		)

		result['pos_list_rows'] = [r for r in pos_list_rs]
		result['count'] = r[2] if len(result['pos_list_rows']) > 0 else 0
		result['page'] = page

		return result

	@cp.expose
	@html
	@db
	@authentication
	@webutil.template('ratinghist.html')
	def ratinghist(self, *args, **kwargs):
		result = { }

		u = kwargs.get('user') or get_username_to_use()

		data = self.rating_hist_data(u)

		result['data'] = webutil.obj_to_json_string(data)
		result['user'] = u

		return result

	@cp.expose
	@html
	@db
	@authentication
	@webutil.template('prefs.html')
	def prefs(self, *args, **kwargs):

		conn = cp.thread_data.conn
		username = get_username_to_use()
		pref_saved = False

		result = {'success' : ''}

		for name, value in kwargs.iteritems():
			# Sanitization:
			if name in DEFAULT_PREFERENCES:
			# Done sanitization.
				pref_saved = True
				sql = '''
					insert into preferences
					(username, name, value)
					values
					(%s, %s, %s)
					on duplicate key update
					value = %s
				'''
				conn.execute(sql, [username, name, value, value])

		if pref_saved:
			result['success'] = 'Saved!'

		return result


	def rating_hist_data(self, u):
		sql = '''
			select * from (
				select 
				unix_timestamp(upm.submittedat) * 1000 as unix1000, 
				upm.ratinguser
				from
				usersposmatchids upm
				join posmatchids pm on pm.posmatchid = upm.posmatchid
				where upm.username = %s
				and pm.version >= %s
				and upm.submittedat > date_add(utc_timestamp(), interval -60 day)
				order by upm.submittedat desc
				limit %s /* Just to limit the max amount of data. */
			) sq
			order by unix1000
		'''

		conn = cp.thread_data.conn

		results = conn.execute(
				sql,
				[
					u,
					conf.POSITIONS_VERSION_TO_USE,
					conf.RATING_HISTORY_MAX_POINTS,
				]
		)

		to_return = [ ]
		for row in results:
			to_return.append([row[0], row[1]])

		return to_return
				


	@cp.expose
	@html
	@db
	@webutil.template('register.html')
	def register(self, *args, **kwargs):

		if get_logged_in_username() is not None:
			raise cp.HTTPRedirect('/')

		result = { }
		conn = cp.thread_data.conn

		message = ''
		error_message = ''

		username = kwargs.get('username')
		password = kwargs.get('password')
		password_again = kwargs.get('password_again')
		email = kwargs.get('email', '')

		if username is not None and password is not None and password_again is not None:

			username = username.strip()
			email = email.strip()

			sql = '''
				select count(*)
				from users
				where username = %s
			'''

			count = conn.execute(sql, [username]).fetchone()[0]

			if username == '':
				error_message = 'Please specify username.'

			elif count != 0:
				error_message = 'Username already exists, please pick another one.'

			elif password == '':
				error_message = 'Please specify password.'

			elif password_again == '':
				error_message = 'Please type password again.'

			elif password != password_again:
				error_message = 'Passwords do not match, please try again.'

			elif email != '' and not gc.validate_email_address(email):
				error_message = 'Invalid email address, please try again.'

			else:
				sql = '''
				insert into users
				(username, pwhash)
				values
				(%s, %s)
				'''
				conn.execute(sql, [username, gc.get_password_hash(password)])
				if email != '':
					sql = '''
					update users
					set email = %s
					where username = %s
					'''
					conn.execute(sql, [email, username])
				cp.session['username'] = username
				raise cp.HTTPRedirect('/')


		result['error_message'] = error_message
		result['message'] = message

		return result

	@cp.expose
	@html
	@ensure_logged_in
	@db
	@authentication
	@webutil.template('cpanel.html')
	def changepass(self, *args, **kwargs):

		current_password = kwargs.get('current_password', '')
		new_password = kwargs.get('new_password', '')
		new_password_again = kwargs.get('new_password_again', '')

		success_message = ''
		error_message = ''

		if current_password == '':
			error_message = 'Please specify the current password.'
		elif new_password == '':
			error_message = 'Please specify the new password.'
		elif new_password_again == '':
			error_message = 'Please specify the new password again.'
		elif new_password != new_password_again:
			error_message = 'New password fields do not match. Please try again.'
		elif not gc.check_username_password(username, current_password):
			error_message = 'Invalid current password. Please try again.'
		else:
			sql = '''
			update users
			set pwhash = %s
			where username = %s
			'''
			cp.thread_data.conn.execute(sql, [gc.get_password_hash(new_password), username])
			cp.session['username'] = username
			success_message = 'Your password has been successfully changed.'

		cp.session['success_message'] = success_message
		cp.session['error_message'] = error_message
		raise cp.HTTPRedirect('/cpanel')

	@cp.expose
	@html
	@ensure_logged_in
	@db
	@authentication
	@webutil.template('cpanel.html')
	def changeemail(self, *args, **kwargs):

		current_password = kwargs.get('current_password', '')
		email = kwargs.get('new_email', '')

		success_message = ''
		error_message = ''

		if current_password == '':
			error_message = 'Please specify the current password.'
		elif not gc.check_username_password(get_logged_in_username(), current_password):
			error_message = 'Invalid current password. Please try again.'
		elif email == '' or not gc.validate_email_address(email):
			error_message = 'Invalid email address, please try again.'
		else:
			sql = '''
			update users
			set email = %s
			where username = %s
			'''
			cp.thread_data.conn.execute(sql, [email, get_logged_in_username()])
			success_message = 'Your email has been successfully set/changed.'

		cp.session['email_success_message'] = success_message
		cp.session['email_error_message'] = error_message
		raise cp.HTTPRedirect('/cpanel')
		
	@cp.expose
	@html
	@ensure_logged_in
	@db
	@authentication
	@webutil.template('cpanel.html')
	def cpanel(self, *args, **kwargs):
		result = { }
		sql = '''
			select 
			email
			from users
			where username = %s
		'''
		users_row = cp.thread_data.conn.execute(sql, [get_logged_in_username()]).fetchone()
		result['current_email'] = users_row[0]
		success_message = cp.session.get('success_message', '')
		error_message = cp.session.get('error_message', '')
		return result

	@cp.expose
	@html
	@db
	@authentication
	@webutil.template('leaderboard.html')
	def leaderboard(self, *args, **kwargs):
		result = { }

		page = int(kwargs.get('page', 1))
		result['page'] = page
		result['query'] = kwargs.get('query')
		return result

	@cp.expose
	@db
	@webutil.rest
	def postcomment(self, *args, **kwargs):
		result = { }

		body = kwargs.get('body', '').strip()
		gnuid = kwargs.get('gnuid')

		if body == '':
			cp.session['comment_post_error_message'] = 'Empty comments are not allowed. Please try again.'
		elif len(body) < 5:
			cp.session['comment_post_error_message'] = 'Too short comment. Please try again.'
		else:
			store_comment(body, gnuid)

		result['comments_html'] = get_comments_html(
				kwargs.get('gnuid'),
				True,
		)
		return result

	@cp.expose
	@db
	@webutil.rest
	def postreport(self, *args, **kwargs):
		result = { }

		body = kwargs.get('body', '').strip()
		gnuid = kwargs.get('gnuid')

		store_report(body, gnuid)

		return result

	@cp.expose
	@html
	@db
	@authentication
	@webutil.template('commentslist.html')
	def commentslist(self, *args, **kwargs):
		result = { }
		page = int(kwargs.get('page', '1'))
		result['page'] = page

		sql = """
			select 

			c1.posmatchid, 
			(
				select 
				c2.username 
				from comments c2
				where c2.posmatchid = c1.posmatchid
				and c2.postedat = max(c1.postedat)
				limit 1
			) latestcommentby,
			max(c1.postedat), 
			count(*),
			(
				select 
				left(c2.comment, %s)
				from comments c2
				where c2.posmatchid = c1.posmatchid
				and c2.postedat = max(c1.postedat)
				limit 1
			) 
			commentsummary,

			case when exists (
				select 1 
				from usersposmatchids upm
				where upm.username = %s and upm.posmatchid = c1.posmatchid
			)
			then 'show' else 'noshow' end

			from comments c1
			join posmatchids pm on pm.posmatchid = c1.posmatchid
			where pm.version >= %s
			group by c1.posmatchid
			order by max(c1.postedat) desc
			limit %s offset %s
		"""

		rs = cp.thread_data.conn.execute(
				sql, 
				[
					conf.COMMENTS_LIST_SUMMARY_LENGTH + 1, 
					get_username_to_use(), 
					conf.POSITIONS_VERSION_TO_USE,
					conf.COMMENTS_LIST_ROWS,
					(page - 1) * conf.COMMENTS_LIST_ROWS,
				],
		)

		result['rs'] = rs
		result['total_comments'] = cp.thread_data.conn.execute(
				"""
				select count(distinct pm.posmatchid)
				from comments c1
				join posmatchids pm on pm.posmatchid = c1.posmatchid
				where pm.version >= %s
				""",
				[conf.POSITIONS_VERSION_TO_USE]
		).fetchone()[0]

		return result

	@cp.expose
	@html
	@db
	@authentication
	@webutil.template('stats.html')
	def stats(self, *args, **kwargs):
		import scipy as sp
		result = { }

		cp.thread_data.conn.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED")

		just_diffs = '''
		select 
		upm.eqdiff, 
		(upm.ratinguser - upm.increment) - (upm.ratingpos + upm.increment)
		from usersposmatchids upm
		where upm.eqdiff is not null
		and upm.increment is not null
		limit 100000
		'''

# First remove the positions where there is no previous rating.
		rows = [r for r in cp.thread_data.conn.execute(just_diffs) if r[1] is not None]
		ratings = [r[1] for r in rows]
		diffs = [r[0] for r in rows]

		rating_quintiles = sp.percentile(ratings, [20, 40, 60, 80])

		result['mean_rating_of_quintile_to_figs'] = { }

		last_quint = -1000
		for quint in rating_quintiles + [100000]:
			diffs = [r[0] for r in rows if last_quint < r[1] < quint]
			ratings = [r[1] for r in rows if last_quint < r[1] < quint]
			mean_rating_of_quintile = sp.mean(ratings)
			if len(diffs) > 0:
				n = len(diffs)
				mean = sp.mean(diffs)
				std = sp.std(diffs)
				quartiles = sp.percentile(diffs, [25, 50, 75])
				last_quint = quint

				figs = { }
				result['mean_rating_of_quintile_to_figs'][mean_rating_of_quintile] = figs
				figs['n'] = n
				figs['mean'] = mean
				figs['std'] = std
				figs['quartiles'] = quartiles

		cp.thread_data.conn.commit()

		return result

def store_comment(body, gnuid):
	sql = '''
		insert into
		comments
		(username, posmatchid, comment, postedat)
		values
		(%s, %s, %s, utc_timestamp())
	'''
	cp.thread_data.conn.execute(sql, [get_logged_in_username(), gnuid, body])

def store_report(body, gnuid):
	sql = '''
		insert into
		reports
		(username, posmatchid, comment, postedat)
		values
		(%s, %s, %s, utc_timestamp())
	'''
	cp.thread_data.conn.execute(sql, [get_username_to_use(), gnuid, body])


@webutil.template('moves.html')
def get_moves_html(**kwargs):
	return kwargs

@webutil.template('comments.html')
def get_comments_html(gnuid, show_comments):
	result = { }
	sql = '''
		select 
		id, username, postedat, comment
		from comments
		where posmatchid = %s
		order by postedat
	'''
	rows = cp.thread_data.conn.execute(sql, [gnuid]).fetchall()
	result['rows'] = rows
	result['position_id'] = gnuid
	result['show_comments'] = show_comments
	return result
	


if __name__ == '__main__':
	logging.basicConfig(level = logging.DEBUG)
	application = Application()
	config_path = gc.get_config_file_path()
	cp.quickstart(
			application,
			'',
			config = config_path
	)

import datetime, collections, logging, os, re

logger = logging.getLogger(__name__)

def sqlite_str_to_date(sqlite_str):
	if sqlite_str is None: return None
	return datetime.date(year = int(sqlite_str[:4]),
		month = int(sqlite_str[5:7]),
		day = int(sqlite_str[-2:])
	)

def get_callers_path():
	"""Returns the path of the file of the module that called 
	this function's calling function"""
	import inspect
	result = os.path.dirname(inspect.getouterframes(inspect.currentframe())[2][1])
	return result

def datetime_to_sqlite_str(dt):
	return datetime.datetime.strftime(
		dt, '%Y-%m-%d %H:%M'
	)



def get_insert_args(table, on_conflict = None, **kwargs):

	def is_j(v):
		return (isinstance(v, tuple) or isinstance(v, list)) and v[1] == 'julian'

	sql = '''
		insert {conflict} into {table}
		({names})
		values
		({question_marks})
		'''
	names = [ ]
	values = [ ]
	for name, value in kwargs.iteritems():
		names.append(name)
		if hasattr(value, 'year') and hasattr(value, 'month') and hasattr(value, 'day'):
			value = date_to_sqlite_str(value)
		values.append(value)
	sql = sql.format(
			table = table,
			names = ', '.join(names),
			question_marks = ', '.join(
				('julianday(?)' if is_j(v) else '?')
				for v in values
			),
			conflict = '' if on_conflict is None else 'or ' + on_conflict,
	)
	values = [v if not is_j(v) else v[0] for v in values]
	logger.debug('get_insert_args sql: %s, args: %s', sql, values)
	return sql, values

class CheckedDictInvalidValueException(Exception):
	pass


class CheckedDict(collections.MutableMapping):
	def __init__(self, validation, initializion = { }):
		self.dict = { }
		self.validation_mapping = validation
		for name, val in initializion.iteritems():
			self[name] = val

	def __setitem__(self, key, val):
		if key in self.validation_mapping:
			if not self.validation_mapping[key](val):
				raise CheckedDictInvalidValueException(
						', '.join(str(_) for _ in (key, val, self.validation_mapping[key]))
				)
		self.dict[key] = val

	def __delitem__(self, key):
		del self.dict[key]

	def __getitem__(self, key):
		return self.dict[key]

	def __iter__(self):
		return iter(self.dict)

	def __len__(self):
		return len(self.dict)

	def __repr__(self):
		return repr(self.dict)

def execute_template(tmpl, dict_, encoding = 'utf-8'):
	try:
		return tmpl.render(output_encoding = encoding, **dict_)
	except:
		import sys
		import cherrypy as cp
		from mako import exceptions
		cp.response.status = 500
		s = exceptions.text_error_template().render(output_encoding = encoding)
		sys.stderr.write(s)
		return exceptions.html_error_template().render(output_encoding = encoding)

def template(path, lookup = None, encoding = 'utf-8'):
	import cherrypy
	import mako.lookup as ml
	if lookup is None:
		lookup = ml.TemplateLookup(directories = [
			get_callers_path()
		])
	def execute_template_(f):
		def t(*args, **kwargs):
			try:
				pars = f(*args, **kwargs)
				return lookup.get_template(path).render(output_encoding = encoding, **pars)
			except cherrypy.HTTPRedirect as r:
				raise
			except Exception as e:
				import sys
				from mako import exceptions
				cherrypy.response.status = 500
				s = exceptions.text_error_template().render(output_encoding = encoding)
				sys.stderr.write(s)
				logger.exception(e)
				if cherrypy.request.config.get('show.stacktraces'):
					return exceptions.html_error_template().render(output_encoding = encoding)
				else:
					h = '''
					<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
					<html><head><title>Error</title></head>
					<body>An internal server error occured.</body>
					</html>
					'''
					return h
					
		return t
	return execute_template_

def obj_to_json_string(obj, indent = None):
	import json
	return json.dumps(
			obj,
			sort_keys = True,
			indent = indent,
	)

def rest(f):
	def f_(self, *args, **kwargs):
		import cherrypy
		cherrypy.response.headers['content-type'] = 'application/json'
		return obj_to_json_string(f(self, *args, **kwargs))
	return f_

unicode_to_html_re = re.compile(r'[\n\f\r]+')
def unicode_to_html(text):
	from mako.filters import html_escape
	text = unicode(html_escape(text))
	text = unicode_to_html_re.sub('<p>', text)
	return text

def truncate_string(s, max_length):
	result = s if len(s) <= max_length else (s[:max_length - 3] + '...')
	return result



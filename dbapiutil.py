import contextlib, logging, time, datetime

logger = logging.getLogger(__name__)

def param_to_sql_literal(param):
    if param is None:
        return 'NULL'
    elif isinstance(param, str):
        return "'" + param.replace("'", "''") + "'"
    elif isinstance(param, int):
        return str(param)
    elif isinstance(param, float):
        return str(param)
    else:
        raise Exception(type(param))

class Connection:

    def __init__(self, dbapi_module, connect_args, connect_kwargs, init_statements):
        self.dbapi_module = dbapi_module
        self.dbapi_conn = dbapi_module.connect(*connect_args, **connect_kwargs)
        if init_statements:
            for statement in init_statements:
                self.execute(statement, [])

    def execute(self, sql, params = (), convert_datetimes = True):
        cursor = self.dbapi_conn.cursor()

        if params and convert_datetimes:
            conv_params = [ ]
            for el in params:
                if isinstance(el, datetime.date) or isinstance(el, datetime.datetime):
                    if el.tzinfo is not None:
                        raise NotImplementedError
                    conv_params.append(el.isoformat())
                else:
                    conv_params.append(el)
            params = conv_params

        params = tuple(param_to_sql_literal(p) for p in params)
        sql = sql % params

        t0 = time.time()
        logger.debug('Starting execution of query: %s', sql)
        cursor.execute(sql)
        t1 = time.time()
        logger.debug('Query execution took %.3f seconds', t1 - t0)

        return cursor

    def explain(self, sql, params = ()):
        return self.execute('explain ' + sql, params)

    def close(self):
        return self.dbapi_conn.close()

    def commit(self):
        return self.dbapi_conn.commit()

    def rollback(self):
        return self.dbapi_conn.rollback()


@contextlib.contextmanager
def connect(dbapi_module, connect_args=(), connect_kwargs={}, init_statements=()):
    conn = None
    try:
        conn = Connection(dbapi_module, connect_args, connect_kwargs, init_statements)
        yield conn
    finally:
        if conn is not None:
            conn.close()


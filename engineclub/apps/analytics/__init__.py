try:
    from redis.connection import UnixDomainSocketConnection, Connection
    from redis import ConnectionPool


    class CacheConnectionPool(object):
        _connection_pool = None

        def get_connection_pool(self, host='127.0.0.1', port=6379, db=1,
                password=None, unix_socket_path=None):

            if self._connection_pool is None:
                connection_class = (
                    unix_socket_path and UnixDomainSocketConnection or Connection
                )
                kwargs = {
                    'db': db,
                    'password': password,
                    'connection_class': connection_class,
                }
                if unix_socket_path is None:
                    kwargs.update({
                        'host': host,
                        'port': port,
                    })
                else:
                    kwargs['path'] = unix_socket_path
                self._connection_pool = ConnectionPool(**kwargs)
            return self._connection_pool

    pool = CacheConnectionPool()

except ImportError:
    pool = None
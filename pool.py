# coding: utf-8

import gevent 
from gevent import monkey
monkey.patch_all()  # support for greenlet

import time
import pymysql
from threading import Lock

import config


class TooManyConnection(Exception):
    """ when too many connection """


class MySQLPool(object):

    def __init__(self):
        self.pool = []
        self.pool_grow_lock = Lock()
        self.max_size = 50  # max size of connection pool

    def _connect(self):
        _config = {
            "host": config.DB_HOST,
            "port": config.DB_PORT,
            "user": config.DB_USER,
            "password": config.DB_PASS,
            "database": config.DB_NAME,
        }
        
        # conn: Representation of a socket with a mysql server.
        conn = pymysql.connect(**_config)
        return conn

    def _get_conn(self):
        for conn, lock in self.pool:
            if lock.acquire(False):
                conn.ping()  # will auto reconnect
                return conn, lock

        # pool need grow
        self.pool_grow_lock.acquire()
        if len(self.pool) < self.max_size:
            conn = self._connect()
            lock = Lock()
            self.pool.append([conn, lock])
            if lock.acquire(False):
                self.pool_grow_lock.release()
                return conn, lock

        self.pool_grow_lock.release()

        return None, None

    def run_sql(self, sql, args=None):
        conn = None
        lock = None
        for i in range(3):
            conn, lock = self._get_conn()
            if conn:
                break
            time.sleep(0.5)

        if not conn:
            raise TooManyConnection("too many connection, pool is exhausted, cannot get connection")

        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
        cursor.execute(sql, args)
        conn.commit()  # always commit here
        
        data = cursor.fetchall()
        cursor.close()
        lock.release()  # give out conn
        
        return data


_pool = MySQLPool()
run_sql = _pool.run_sql

__all__ = ["run_sql"]


""" test part """
if __name__ == "__main__":
    
    # print run_sql("select * from user;")
   
    import gevent 
    from gevent import monkey
    monkey.patch_all()

    jobs = []
    for i in range(10):
        jobs.append(gevent.spawn(run_sql, "select * from user;"))

    gevent.joinall(jobs)
    for i in jobs:
        print i.value
    
    """
    from threading import Thread
   
    for i in range(100):
        t = Thread(target=run_sql, args=("select * from user;", ))
        t.start()
    """


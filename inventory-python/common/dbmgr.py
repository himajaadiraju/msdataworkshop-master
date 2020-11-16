# Database Manager

import os
import sys
import logging
from os import environ as env
import cx_Oracle
import threading
import time

# Parameters
db_connection_count = int(env.get("DB_CONNECTION_COUNT", "1"))
db_user =             env.get('DB_USER').strip()
db_password =         env.get('DB_PASSWORD').strip()
db_connect_string =   env.get('DB_CONNECT_STRING')

readyfile = ""
logger = None
pool = None

# Set ready file name (must correspond with name in app.yaml)
def setReadyFileName(fileName):
    global readyfile
    readyfile = fileName

# Start the Database Manager thread
def start(name):
    global logger
    logger = logging.getLogger(name)
    t = threading.Thread(None, run, name)
    t.daemon = True
    t.start()

# Acquire connection from pool
def acquireConn():
    global pool
    if pool:
        try:
            conn = pool.acquire()
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            # ORA-12514: TNS:listener does not currently know of service requested in connect descriptor
            # ORA-12757: instance does not currently know of requested service
            # ORA-12541: TNS:no listener
            if error.code in [12514, 12757, 12541]:
                reportDown(error.code)
                raise DatabaseDown()
            else:
                raise
        else:
            return conn
    else:
        raise DatabaseDown()

# Release connection back to pool
def releaseConn(conn):
    global pool
    if pool and conn:
        try:
            pool.release(conn)
        except:
            pass

# Database Manager Thread
def run():
    global pool
    while True:
        if pool:
            time.sleep(10)
            continue

        logger.debug("Create Connection Pool Started")
        try:
            pool = cx_Oracle.SessionPool(
                db_user,
                db_password,
                db_connect_string,
                externalauth = False if db_password else True,
                encoding="UTF-8",
                min=db_connection_count,
                max=db_connection_count,
                increment=0,
                threaded=True,
                events=True,
                getmode=cx_Oracle.SPOOL_ATTRVAL_TIMEDWAIT,
                waitTimeout=10000)

        except cx_Oracle.DatabaseError as e:
            error, = e.args
            # ORA-12514: TNS:listener does not currently know of service requested in connect descriptor
            # ORA-12757: instance does not currently know of requested service
            # ORA-12541: TNS:no listener
            if error.code in [12514, 12757, 12541]:
                reportDown(error.code)
            else:
                raise
        else:
            logger.debug("Create Connection Pool Ended")
            reportUp()
        finally:
            time.sleep(10)

# Report the service down (see app.yaml)
def reportDown(errno):
    global pool
    if pool:
        pool = None
        os.remove(readyfile)
    logger.debug(f"Database Reported Down Error {errno}")

# Report the service up (see app.yaml)
def reportUp():
    open(readyfile, "w+").close()
    logger.debug("Database Reported Up")

# DatabaseDown Exception
class DatabaseDown(Exception):
    def __init__(self):
        pass


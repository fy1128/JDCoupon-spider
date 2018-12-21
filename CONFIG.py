import os

MYSQL_DB_HOST = os.environ['MYSQL_DB_HOST'] if 'MYSQL_DB_HOST' in os.environ else '127.0.0.1'
MYSQL_DB_USER = os.environ['MYSQL_DB_USER'] if 'MYSQL_DB_USER' in os.environ else 'root'
MYSQL_DB_NAME = os.environ['MYSQL_DB_NAME'] if 'MYSQL_DB_NAME' in os.environ else 'jd'
MYSQL_DB_PASS = os.environ['MYSQL_DB_PASS'] if 'MYSQL_DB_PASS' in os.environ else '123456'
MYSQL_DB_PORT = int(os.environ['MYSQL_DB_PORT']) if 'MYSQL_DB_PORT' in os.environ else 3306

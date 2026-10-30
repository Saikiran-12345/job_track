"""
JobTrack Configuration Package Initialization.

Registers PyMySQL as the MySQLdb driver so Django's MySQL database
backend communicates smoothly with MySQL 8.0 across platforms.
"""

import pymysql

pymysql.install_as_MySQLdb()

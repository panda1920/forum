# -*- coding: utf-8 -*-
"""
Script to insert data in mongo
Data is based on content of dbdata.json
"""

import logging
import os

from tests.database.setup_crudmanager import Setup_MongoCrudManager

MONGO_ISTEST = True
PROD_MONGOHOSTNAME = 'localhost'
PROD_MONGOPORTNUM = '3000'


def modify_environ():
    if not MONGO_ISTEST:
        os.environ['MONGO_HOSTNAME'] = PROD_MONGOHOSTNAME
        os.environ['MONGO_PORT'] = PROD_MONGOPORTNUM


def insert_data():
    print('Freshly inserting data into mongodb')
    try:
        dbname = os.environ.get('MONGO_DBNAME', 'TEST_MYFORUMWEBAPP')
        setup = Setup_MongoCrudManager(dbname)
        setup.cleanup()
        setup.setup()
        print('Data insertion completed')
    except Exception as e:
        print('Failed to complete data insertion')
        logging.error(e)


if __name__ == '__main__':
    modify_environ()
    insert_data()

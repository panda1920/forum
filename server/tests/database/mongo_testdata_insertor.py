# -*- coding: utf-8 -*-
"""
Script to insert data in mongo
Data is based on content of testdata.json
"""

import logging
import os

from tests.database.setup_crudmanager import Setup_MongoCrudManager


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
    insert_data()

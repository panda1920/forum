# -*- coding: utf-8 -*-
"""
Script to insert data in mongo
Data is based on content of testdata.json
"""

import logging

from tests.database.setup_crudmanager import Setup_MongoCrudManager


def insert_data():
    print('Freshly inserting data into mongodb')
    try:
        setup = Setup_MongoCrudManager()
        setup.cleanup()
        setup.setup()
        print('Data insertion completed')
    except Exception as e:
        print('Failed to complete data insertion')
        logging.error(e)


if __name__ == '__main__':
    insert_data()

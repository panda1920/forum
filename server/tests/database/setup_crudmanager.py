# -*- coding: utf-8 -*-
"""
This file contains classes to help setup/cleanup needed for
testing database CRUD management classes
"""

import os
import json
import shutil
from pathlib import Path

from pymongo import MongoClient

from server.database.file_crudmanager import FileCrudManager
from server.database.mongo_crudmanager import MongoCrudManager
import tests.mocks as mocks

PROJECT_DIR = Path(__file__).resolve().parents[3]
TESTDATA = PROJECT_DIR / 'server' / 'tests' / 'database' / 'testdata.json'


class SetupCrudManager:
    def setup(self):
        """
        Method to setup database management class
        """
        raise NotImplementedError

    def cleanup(self):
        """
        Method to cleanup database management class
        """
        raise NotImplementedError

    def teardown(self):
        """
        Method to call when all tests in file finished
        """
        raise NotImplementedError

    def validateCreatedUsers(self):
        """
        validates user created in the database
        """
        raise NotImplementedError

    def validateCreatedPosts(self):
        """
        validates posts created in the database
        """
        raise NotImplementedError

    def getAllUsers(self):
        """
        returns a list of objects
        retrieves all users in database
        """
        raise NotImplementedError

    def getUserCount(self):
        """
        returns the number of users in the current db
        """
        raise NotImplementedError

    def findUsers(self, fieldname, fieldvalues):
        """
        returns all users that match the criteria
        """
        raise NotImplementedError

    def getOriginalUsers(self):
        """
        returns a list of objects
        retrieves all users that were in testdata file
        """
        raise NotImplementedError

    def getAllPosts(self):
        """
        returns a list of objects
        retrieves all posts in database
        """
        raise NotImplementedError

    def getPostCount(self):
        """
        returns the number of posts in the current db
        """
        raise NotImplementedError

    def findPosts(self, fieldname, fieldvalues):
        """
        returns all posts that match the criteria
        """
        raise NotImplementedError

    def getOriginalPosts(self):
        """
        returns a list of objects
        retrieves all posts that were in testdata file
        """
        raise NotImplementedError

    def getMockUserAuth(self):
        """
        returns a mock instance of user authentication class
        this is a depdency that is injected into database manager at its construction
        """
        raise NotImplementedError

    def getDB(self):
        """
        returns the instance of database manager class
        this gives access to what we want to test
        """
        raise NotImplementedError

    def getCounter(self, fieldname):
        """
        returns the current countervalue associated with fieldname
        
        Args:
            fieldname (str): specify which fieldname
        Returns:
            (int)
        """
        raise NotImplementedError


class Setup_FileCrudManager(SetupCrudManager):
    def __init__(self):
        self._saveLocation = Path(__file__).resolve().parents[0] / 'temp'
        self._usersFile = self._saveLocation / FileCrudManager.USERS_FILENAME
        self._postsFile = self._saveLocation / FileCrudManager.POSTS_FILENAME
        self._countersFile = self._saveLocation / FileCrudManager.COUNTERS_FILENAME
        self._testdata = self._readTestData()
        self._userauth = mocks.createMockUserAuth()
        self._db = FileCrudManager(self._saveLocation, self._userauth)

    def setup(self):
        self._saveLocation.mkdir(exist_ok=True)
        self._writeObjToFile(self._testdata['users'], self._usersFile)
        self._writeObjToFile(self._testdata['posts'], self._postsFile)
        self._writeObjToFile(self._testdata['counters'], self._countersFile)

    def cleanup(self):
        shutil.rmtree(self._saveLocation, ignore_errors=True)

    def teardown(self):
        pass

    def validateCreatedUsers(self):
        createdUsers = self.getAllUsers()
        assert self._usersFile.exists()
        assert len(createdUsers) == len(self.getOriginalUsers())

    def validateCreatedPosts(self):
        assert self._postsFile.exists()
        assert len(self.getAllPosts()) == len(self.getOriginalPosts())

    def getAllUsers(self):
        return self._readJson( self._usersFile )

    def getUserCount(self):
        return len( self.getAllUsers() )

    def getOriginalUsers(self):
        return self._testdata['users']

    def findUsers(self, fieldname, fieldvalues):
        return [
            user for user in self.getAllUsers()
            if user[fieldname] in fieldvalues
        ]

    def getAllPosts(self):
        return self._readJson( self._postsFile )

    def getPostCount(self):
        return len( self.getAllPosts() )

    def findPosts(self, fieldname, fieldvalues):
        return [
            post for post in self.getAllPosts()
            if post[fieldname] in fieldvalues
        ]

    def getOriginalPosts(self):
        return self._testdata['posts']

    def getDB(self):
        return self._db

    def getCounter(self, fieldname):
        counters = self._readJson(self._countersFile)
        for counter in counters:
            if counter['fieldname'] == fieldname:
                return counter['value']
        return None

    def getMockUserAuth(self):
        return self._userauth

    def _readTestData(self):
        with TESTDATA.open('r', encoding='utf-8') as f:
            return json.load(f)

    def _writeObjToFile(self, obj, fileName):
        fileName.touch()
        with fileName.open('w', encoding='utf-8') as f:
            json.dump(obj, f)

    def _readJson(self, filepath):
        with filepath.open('r', encoding='utf-8') as f:
            return json.load(f)


class Setup_MongoCrudManager(SetupCrudManager):
    TEST_DBNAME = 'test_mongo'

    def __init__(self, dbname=None):
        if dbname is None:
            dbname = self.TEST_DBNAME
        self._dbname = dbname
        self._userauth = mocks.createMockUserAuth()
        self._db = MongoCrudManager(dbname, self._userauth)

        hostname = os.getenv('MONGO_HOSTNAME')
        port = int( os.getenv('MONGO_PORT') )
        self._mongo = MongoClient(host=hostname, port=port)
        self._testdata = self._readJson(TESTDATA)

    def setup(self):
        db = self._getDB()
        db['users'].insert_many(self._testdata['users'])
        db['posts'].insert_many(self._testdata['posts'])
        db['counters'].insert_many(self._testdata['counters'])

    def cleanup(self):
        db = self._getDB()
        db['users'].delete_many({})
        db['posts'].delete_many({})
        db['counters'].delete_many({})

    def teardown(self):
        self._mongo.drop_database(self._dbname)
        self._mongo.close()

    def validateCreatedUsers(self):
        assert len(self.getAllUsers()) == len(self.getOriginalUsers())

    def validateCreatedPosts(self):
        assert len(self.getAllPosts()) == len(self.getOriginalPosts())

    def getAllUsers(self):
        return list( self._getDB()['users'].find() )

    def getUserCount(self):
        return self._getDB()['users'].count_documents({})

    def getOriginalUsers(self):
        return self._testdata['users']

    def findUsers(self, fieldname, fieldvalues):
        query = { fieldname: { '$in': fieldvalues } }
        return list( self._getDB()['users'].find(query) )

    def getAllPosts(self):
        return list( self._getDB()['posts'].find() )

    def getPostCount(self):
        return self._getDB()['posts'].count_documents({})

    def findPosts(self, fieldname, fieldvalues):
        query = { fieldname: { '$in': fieldvalues } }
        return list( self._getDB()['posts'].find(query) )

    def getOriginalPosts(self):
        return self._testdata['posts']

    def getDB(self):
        return self._db

    def getCounter(self, fieldname):
        query = dict(
            fieldname={'$eq': fieldname}
        )
        return self._getDB()['counters'].find_one(query)['value']

    def getMockUserAuth(self):
        return self._userauth

    def _readJson(self, filepath):
        with filepath.open('r', encoding='utf-8') as f:
            return json.load(f)

    def _getDB(self):
        # not to be confused with getDB (without the underscore)
        # this acquires the database instance from pymongo
        return self._mongo[self._dbname]

# -*- coding: utf-8 -*-
"""
This file houses logic to create test data for this application
Currently creating 3 kinds of data:
    - user
    - post
    - counter
"""


import json
from pathlib import Path
from time import time

from server.services.userauth import UserAuthentication


class DataCreator:
    USERS = [
        'Anonymous',
        'Bobby',
        'Charlie',
        'Daniel',
        'Eugene',
        'Frederick',
        'Geralt',
        'Henry',
        'Ian',
        'Johnson',
    ]
    EMAIL_DOMAIN = '@myforumwebapp.com'
    POSTCOUNT_PER_USER_ENG = 48
    POSTCOUNT_PER_USER_JPN = 2
    POSTCOUNT_PER_USER = POSTCOUNT_PER_USER_ENG + POSTCOUNT_PER_USER_JPN
    PLACEHOLDER_IMG_URL = 'https://upload.wikimedia.org/wikipedia/en/b/b1/Portrait_placeholder.png'

    def __init__(self, testDataPath):
        self._testDataPath = testDataPath

    def createTestData(self):
        self._testDataPath.unlink()
        self._testDataPath.touch()

        users = self._createUsers()
        posts = self._createPosts(users)
        counters = self._createCounters()

        with self._testDataPath.open('w', encoding='utf-8') as f:
            json.dump({
                'users': users,
                'posts': posts,
                'counters': counters,
            }, f)

    def _createUsers(self):
        users = []
        now = time()
        for idx, username in enumerate(self.USERS):
            users.append({
                'userId': str(idx),
                'displayName': username,
                'userName': username.lower() + self.EMAIL_DOMAIN,
                'password': UserAuthentication.hashPassword('12345678'),
                'createdAt': now,
                'imageUrl': self.PLACEHOLDER_IMG_URL,
            })
        
        return users

    def _createPosts(self, users):
        posts = []
        now = time()

        for userCount, user in enumerate(users):
            for n in range(self.POSTCOUNT_PER_USER):
                postId = str(userCount * self.POSTCOUNT_PER_USER + n)

                if n < self.POSTCOUNT_PER_USER_ENG:
                    posts.append(self._createEnglishPost(
                        user, n, postId, now
                    ))
                else:
                    posts.append(self._createJapanesePost(
                        user, n, postId, now
                    ))

        return posts

    def _createEnglishPost(self, user, postNum, postId, createdAt):
        return {
            'postId': postId,
            'userId': user['userId'],
            'content': f'{user["displayName"]}\'s post {postNum}',
            'createdAt': createdAt
        }

    def _createJapanesePost(self, user, postNum, postId, createdAt):
        return {
            'postId': postId,
            'userId': user['userId'],
            'content': f'ユーザ名：{user["displayName"]}による{postNum}番目の投稿です',
            'createdAt': createdAt
        }

    def _createCounters(self):
        return [
            dict( fieldname='userId', value=len( self.USERS ) ),
            dict( fieldname='postId', value=self.getTotalPostCount() ),
        ]

    @classmethod
    def getUsernames(cls):
        return cls.USERS

    @classmethod
    def getPostCountPerUser(cls):
        return cls.POSTCOUNT_PER_USER

    @classmethod
    def getTotalPostCount(cls):
        return len(cls.USERS) * cls.POSTCOUNT_PER_USER


if __name__ == '__main__':
    DEFAULT_FILENAME = Path(__file__).resolve().parents[0] / 'testdata.json'
    DataCreator(DEFAULT_FILENAME).createTestData()

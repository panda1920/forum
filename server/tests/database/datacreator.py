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

from server.services.userauth import PasswordService


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
    PLACEHOLDER_IMG_URL = 'https://upload.wikimedia.org/wikipedia/en/b/b1/Portrait_placeholder.png'
    THREAD_COUNT = len(USERS)
    POSTCOUNT_PER_THREAD_ENG = 2
    POSTCOUNT_PER_THREAD_JPN = 1
    POSTCOUNT_PER_THREAD = POSTCOUNT_PER_THREAD_ENG + POSTCOUNT_PER_THREAD_JPN
    POSTCOUNT_PER_USER = POSTCOUNT_PER_THREAD * THREAD_COUNT

    def __init__(self, testDataPath):
        self._testDataPath = testDataPath

    def createTestData(self):
        self._testDataPath.unlink()
        self._testDataPath.touch()

        users = self._createUsers()
        threads = self._createThreads(users)
        posts = self._createPosts(users, threads)
        counters = self._createCounters()

        with self._testDataPath.open('w', encoding='utf-8') as f:
            json.dump({
                'users': users,
                'posts': posts,
                'threads': threads,
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
                'password': PasswordService.hashPassword('12345678'),
                'createdAt': now,
                'imageUrl': self.PLACEHOLDER_IMG_URL if idx == 0 else f'https://randomuser.me/api/portraits/men/{idx}.jpg'
            })
        
        return users

    def _createThreads(self, users):
        threads = []
        now = time()
        for idx, user in enumerate(users):
            threads.append(dict(
                threadId=str(idx),
                userId=user['userId'],
                title=f'{user["displayName"]}\'s thread',
                subject='Subject of this thread',
                createdAt=now,
            ))

        return threads

    def _createPosts(self, users, threads):
        posts = []
        postCreatedCount = 0
        now = time()

        # for each user create posts in a way that
        # posts for each threads
        # some english post in thread
        # some japanese post in thread

        for userCount, user in enumerate(users):
            for threadCount, thread in enumerate(threads):
                postNum = threadCount * self.POSTCOUNT_PER_THREAD
                for engCount in range(self.POSTCOUNT_PER_THREAD_ENG):
                    posts.append(
                        self._createEnglishPost(user, thread, postNum, postCreatedCount, now)
                    )
                    postCreatedCount += 1
                    postNum += 1

                for jpnCount in range(self.POSTCOUNT_PER_THREAD_JPN):
                    posts.append(
                        self._createJapanesePost(user, thread, postNum, postCreatedCount, now)
                    )
                    postCreatedCount += 1
                    postNum += 1

        return posts

    def _createEnglishPost(self, user, thread, postNum, postId, createdAt):
        return {
            'postId': postId,
            'userId': user['userId'],
            'threadId': thread['threadId'],
            'content': f'{user["displayName"]}\'s post {postNum}',
            'createdAt': createdAt
        }

    def _createJapanesePost(self, user, thread, postNum, postId, createdAt):
        return {
            'postId': postId,
            'userId': user['userId'],
            'threadId': thread['threadId'],
            'content': f'ユーザ名：{user["displayName"]}による{postNum}番目の投稿です',
            'createdAt': createdAt
        }

    def _createCounters(self):
        return [
            dict( fieldname='userId', value=len( self.USERS ) ),
            dict( fieldname='postId', value=self.getTotalPostCount() ),
            dict( fieldname='threadId', value=self.getTotalThreadCount() ),
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

    @classmethod
    def getTotalThreadCount(cls):
        return cls.THREAD_COUNT


if __name__ == '__main__':
    DEFAULT_FILENAME = Path(__file__).resolve().parents[0] / 'testdata.json'
    DataCreator(DEFAULT_FILENAME).createTestData()

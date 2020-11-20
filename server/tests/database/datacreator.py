# -*- coding: utf-8 -*-
"""
This file houses logic to create test data for this application
Currently creating the following data:
    - user
    - post
    = threads
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
    BOARD_COUNT = 3
    THREADCOUNT_PER_BOARD = 5
    POSTCOUNT_PER_THREAD_ENG = 2
    POSTCOUNT_PER_THREAD_JPN = 1
    POSTCOUNT_PER_USERTHREAD = POSTCOUNT_PER_THREAD_ENG + POSTCOUNT_PER_THREAD_JPN

    def __init__(self, testDataPath):
        self._testDataPath = testDataPath

    def createTestData(self):
        self._testDataPath.unlink()
        self._testDataPath.touch()

        users = self._createUsers()
        boards = self._createBoards(users)
        threads = self._createThreads(users, boards)
        posts = self._createPosts(users, threads)
        counters = self._createCounters()

        with self._testDataPath.open('w', encoding='utf-8') as f:
            json.dump({
                'users': users,
                'posts': posts,
                'threads': threads,
                'boards': boards,
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

    def _createBoards(self, users):
        boards = []
        now = time()

        for idx in range(self.BOARD_COUNT):
            user = users[idx]
            boards.append(dict(
                boardId=str(idx),
                userId=user['userId'],
                title=f'{user["displayName"]}\'s Board',
                createdAt=now,
            ))

        return boards

    def _createThreads(self, users, boards):
        threads = []
        now = time()
        
        for board_idx, board in enumerate(boards):
            for idx in range(self.THREADCOUNT_PER_BOARD):
                user = users[idx]
                threads.append(dict(
                    boardId=board['boardId'],
                    threadId=str(idx + board_idx * self.THREADCOUNT_PER_BOARD),
                    lastPostId=None,
                    userId=user['userId'],
                    title=f'{user["displayName"]}\'s thread',
                    subject='Subject of this thread',
                    views=0,
                    createdAt=now,
                ))
            board['threadCount'] = self.THREADCOUNT_PER_BOARD

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
                postNum = threadCount * self.POSTCOUNT_PER_USERTHREAD
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

                thread['lastPostId'] = posts[-1]['postId']
                thread['postCount'] = self.POSTCOUNT_PER_USERTHREAD * len(self.USERS)
        return posts

    def _createEnglishPost(self, user, thread, postNum, postId, createdAt):
        return {
            'postId': str(postId),
            'userId': user['userId'],
            'threadId': thread['threadId'],
            'content': f'{user["displayName"]}\'s post {postNum}',
            'createdAt': createdAt
        }

    def _createJapanesePost(self, user, thread, postNum, postId, createdAt):
        return {
            'postId': str(postId),
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
            dict( fieldname='boardId', value=self.getTotalBoardCount() ),
        ]

    @classmethod
    def getUsernames(cls):
        return cls.USERS

    @classmethod
    def getTotalPostCount(cls):
        return len(cls.USERS) * cls.POSTCOUNT_PER_USERTHREAD * cls.getTotalThreadCount()

    @classmethod
    def getTotalThreadCount(cls):
        return cls.THREADCOUNT_PER_BOARD * cls.getTotalBoardCount()

    @classmethod
    def getTotalBoardCount(cls):
        return cls.BOARD_COUNT


if __name__ == '__main__':
    DEFAULT_FILENAME = Path(__file__).resolve().parents[0] / 'testdata.json'
    DataCreator(DEFAULT_FILENAME).createTestData()

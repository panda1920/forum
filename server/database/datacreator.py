import json
from pathlib import Path
from time import time

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
    POSTCOUNT_PER_USER = 200

    def __init__(self, testDataPath):
        self._testDataPath = testDataPath

    def createTestData(self):
        self._testDataPath.unlink()
        self._testDataPath.touch()

        users = self.createUsers()
        posts = self.createPosts(users)

        with self._testDataPath.open('w', encoding='utf-8') as f:
            json.dump({
                'users': users,
                'posts': posts
            }, f)

    def createUsers(self):
        users = []
        now = time()
        for idx, username in enumerate(self.USERS):
            users.append({
                'userId': str(idx),
                'displayName': username,
                'userName': username.lower() + self.EMAIL_DOMAIN,
                'createdAt': now
            })
        
        return users

    def createPosts(self, users):
        posts = []
        now = time()

        for userCount, user in enumerate(users):
            for n in range(self.POSTCOUNT_PER_USER):
                posts.append({
                    'postId': str(userCount * self.POSTCOUNT_PER_USER + n),
                    'userId': user['userId'],
                    'post': f'{user["displayName"]}\'s post {n}',
                    'createdAt': now
                })

        return posts

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
    DEFAULT_FILENAME = Path(__file__).resolve().parents[0] / 'tests' / 'testdata.json'
    DataCreator(DEFAULT_FILENAME).createTestData()
import json
import time

from .database import Database

class SimpleFile(Database):
    USERS_FILENAME = 'users.json'
    POSTS_FILENAME = 'posts.json'
    THREADS_FILENAME = 'threads.json'

    def __init__(self, filePath):
        self._saveLocation = filePath

    def createUser(self, userProps):
        usersFile = self._saveLocation / self.USERS_FILENAME

        with usersFile.open('r', encoding='utf-8') as f:
            data = json.load(f)

        userData = userProps
        userData['createdAt'] = time.time()
        data.append(userData)

        with usersFile.open('w') as f:
            json.dump(data, f)

    def searchUser(self, searchCritera):
        pass

    def deleteUser(self, userId):
        usersFile = self._saveLocation / self.USERS_FILENAME

        with usersFile.open('r', encoding='utf-8') as f:
            data = json.load(f)

        data = [ user for user in data if user['userId'] != userId ]

        with usersFile.open('w') as f:
            json.dump(data, f)

    def createPost(self, post):
        postsFile = self._saveLocation / self.POSTS_FILENAME

        with postsFile.open('r', encoding='utf-8') as f:
            data = json.load(f)

        postData = post
        postData['createdAt'] = time.time()
        data.append(postData)

        with postsFile.open('w') as f:
            json.dump(data, f)
    
    def searchPost(self, searchCriteria):
        pass

    def deletePost(self, postId):
        postsFile = self._saveLocation / self.POSTS_FILENAME

        with postsFile.open('r', encoding='utf-8') as f:
            data = json.load(f)

        data = [ post for post in data if post['postId'] != postId ]

        with postsFile.open('w') as f:
            json.dump(data, f)
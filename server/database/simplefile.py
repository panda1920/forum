import json
import time

from .database import Database

class SimpleFile(Database):
    USERS_FILENAME = 'users.json'
    POSTS_FILENAME = 'posts.json'
    THREADS_FILENAME = 'threads.json'

    def __init__(self, filePath):
        self._saveLocation = filePath
        self._usersFile = self.createIfNotExist(self._saveLocation / self.USERS_FILENAME)
        self._postsFile = self.createIfNotExist(self._saveLocation / self.POSTS_FILENAME)
        self._threadsFile = self.createIfNotExist(self._saveLocation / self.THREADS_FILENAME)

    def createIfNotExist(self, filePath):
        if not filePath.exists():
            with filePath.open('w', encoding='utf-8') as f:
                json.dump([], f)

        return filePath

    def createUser(self, userProps):
        with self._usersFile.open('r', encoding='utf-8') as f:
            data = json.load(f)

        userData = userProps
        userData['createdAt'] = time.time()
        data.append(userData)

        with self._usersFile.open('w') as f:
            json.dump(data, f)

    def searchUser(self, searchCritera):
        pass

    def deleteUser(self, userIds):
        with self._usersFile.open('r', encoding='utf-8') as f:
            users = json.load(f)

        filteredUsers = [
            user for user in users
            if user['userId'] not in userIds
        ]

        with self._usersFile.open('w') as f:
            json.dump(filteredUsers, f)

        postsToDelete = self.searchPost({
            'userId': userIds
        })
        self.deletePost( [post['postId'] for post in postsToDelete] )

    def createPost(self, post):
        with self._postsFile.open('r', encoding='utf-8') as f:
            data = json.load(f)

        postData = post
        postData['createdAt'] = time.time()
        data.append(postData)

        with self._postsFile.open('w') as f:
            json.dump(data, f)
    
    def searchPost(self, searchCriteria):
        with self._postsFile.open('r', encoding='utf-8') as f:
            posts = json.load(f)

        return [post for post in posts if self.matchesCriteria(post, searchCriteria)]

    def matchesCriteria(self, post, searchCriteria):
        for field, values in searchCriteria.items():
            for value in values:
                if post[field] == value:
                    return True

        return False

    def deletePost(self, postIds):
        with self._postsFile.open('r', encoding='utf-8') as f:
            data = json.load(f)

        data = [ post for post in data if post['postId'] not in postIds ]

        with self._postsFile.open('w') as f:
            json.dump(data, f)
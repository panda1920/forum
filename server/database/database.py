from server.database.paging import Paging

class Database:
    def __init__(self):
        pass

    def createUser(self, user):
        pass

    def searchUser(self, searchCritera, paging = Paging()):
        pass

    def deleteUser(self, userIds):
        pass
    
    def createPost(self, post):
        pass
    
    def searchPost(self, searchFilters, paging = Paging()):
        pass

    def deletePost(self, postIds):
        pass

    def updatePost(self, post):
        pass


def getDB(app):
    return app.config['DATABASE_OBJECT']

def getFilter(app):
    return app.config['SEARCH_FILTER']

def getPaging(app):
    return app.config['PAGING']
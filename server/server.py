from flask import Flask

def setupApp():
    app = Flask(__name__)
    
    from routes import routes
    app.register_blueprint(routes)

    from database.database import Database
    app.config['DATABASE_OBJECT'] = Database()

    return app
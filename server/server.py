from flask import Flask
from server.config import Config

def setupApp():
    app = Flask(__name__)
    
    from server.routes import routes
    app.register_blueprint(routes)

    app.config.from_object(Config)

    return app
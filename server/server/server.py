from flask import Flask

from server.config import Config
from server.log_setup import setup


def setupApp():
    app = Flask(__name__)
    
    import server.routes.misc_routes
    import server.routes.posts_routes
    import server.routes.users_routes
    import server.routes.thread_routes
    import server.routes.boards_routes
    app.register_blueprint(server.routes.misc_routes.routes)
    app.register_blueprint(server.routes.posts_routes.routes)
    app.register_blueprint(server.routes.users_routes.routes)
    app.register_blueprint(server.routes.thread_routes.routes)
    app.register_blueprint(server.routes.boards_routes.routes)

    app.config.from_object(Config)

    # setup logger
    setup()

    return app

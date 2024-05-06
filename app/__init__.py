from flask import Flask
# from config import config
from app import main
# from dotenv import load_dotenv

def create_app():
    # load_dotenv()  # Load environment variables from .env file
    app = Flask(__name__, static_folder="static")
    # app.config.from_object(config)
    app.register_blueprint(main.bp)

    return app

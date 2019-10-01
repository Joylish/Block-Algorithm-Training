from Tools.scripts.parse_html5_entities import get_json
from flask import Flask, request, jsonify
import datetime


app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()

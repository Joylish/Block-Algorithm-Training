from Tools.scripts.parse_html5_entities import get_json
from flask import Flask, request, jsonify, url_for
import datetime
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'this is secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///BlockSolve.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = "Problem"
    pid = db.Column(db.BigInteger, primary_key=True)
    title = db.Column(db.String, unique=True)
    createdAt = db.Column(db.DateTime)
    creator = db.Column(db.String(256))
    # category는 index번호로 표시한다( 1: basic 2: stack ..)
    category =  db.Column(db.Integer())
    content = db.Column(db.String)
    inputDetail = db.Column(db.String)
    outputDetail = db.Column(db.String)
    numSubmission = db.Column(db.Integer)
    correctRate = db.Column(db.REAL)
    initXML = db.Column(db.JSON)

    def __init__(self, username, password, bank_password, deposit_amount):
        self.username = username
        self.password = generate_password_hash(password)
        self.bank_password = bank_password
        self.deposit = deposit_amount

@app.route('/')
def hello_world():
    return 'Welcome'

@app.route('/problems', methods=['GET'])
def view_problems():
    return

@app.route('/problems/<pid>', methods=['GET'])
def view_each_problem():
    dt = dict
    return jsonify(dt)

if __name__ == '__main__':
    app.run()

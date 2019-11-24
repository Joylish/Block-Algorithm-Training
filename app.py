
# -*- coding: utf-8 -*-
from operator import itemgetter
from flask import Flask, request, jsonify
import json

from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import pandas as pd

app = Flask(__name__)
cors = CORS(app)

app.config['SECRET_KEY'] = 'this is secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///BlockSolve.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Problem(db.Model):
    __tablename__ = "Problem"
    id = db.Column(db.BigInteger, primary_key=True, autoincrement= True, nullable= False)
    title = db.Column(db.String, nullable= False)
    createdAt = db.Column(db.Integer, nullable= False)
    creator = db.Column(db.String(256), nullable= False)
    category = db.Column(db.String(256))
    content = db.Column(db.Text, nullable= False)
    inputDetail = db.Column(db.Text, nullable= False)
    outputDetail = db.Column(db.Text, nullable= False)
    numSub = db.Column(db.Integer)
    correctRate = db.Column(db.Float)
    initXML = db.Column(db.Text)

    example = db.relationship('Example', backref='Problem', cascade='all, delete, delete-orphan')
    userSolution = db.relationship('UserSolution', backref='Problem', cascade='all, delete, delete-orphan')
    testCase = db.relationship('TestCase', backref='Problem', cascade='all, delete, delete-orphan')

    def __init__(self, id, title, createdAt, creator,
                 category, content, inputDetail, outputDetail,
                 numSub, correctRate, initXML):
        self.id = id
        self.title = title
        self.createdAt = createdAt
        self.creator = creator
        self.category = category
        self.content = content
        self.inputDetail = inputDetail
        self.outputDetail = outputDetail
        self.numSub = numSub
        self.correctRate = correctRate
        self.initXML = initXML

class Example(db.Model):
    __tablename__ = "Example"
    id = db.Column(db.BigInteger, primary_key= True, autoincrement= True, nullable= False)
    pid = db.Column(db.ForeignKey('Problem.id'), nullable= False)
    input = db.Column(db.Text, nullable= False)
    output = db.Column(db.Text, nullable= False)

    def __init__(self, id, pid, input, output):
        self.id = id
        self.pid = pid
        self.input = input
        self.output = output

class User(db.Model):
    __tablename__ = "User"
    id = db.Column(db.BigInteger, primary_key= True, autoincrement= True, nullable= False)
    name = db.Column(db.String, nullable= False)
    createdAt = db.Column(db.Integer, nullable= False)
    email = db.Column(db.String, nullable= False)

    userSolution = db.relationship('UserSolution', backref='User', cascade='all, delete, delete-orphan')

    def __init__(self, id, name, createdAt, email):
        self.id = id
        self.name = name
        self.createdAt = createdAt
        self.email = email

class TestCase(db.Model):
    __tablename__ = "TestCase"
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True, nullable=False)
    pid = db.Column(db.BigInteger, db.ForeignKey('Problem.id'), nullable= False)
    input = db.Column(db.Text, nullable= False)
    output = db.Column(db.Text, nullable= False)

    testResult = db.relationship('TestResult', backref='TestCase', cascade='all, delete, delete-orphan')

    def __init__(self, id, pid, input, output):
        self.id = id
        self.pid = pid
        self.input = input
        self.output = output

class TestResult(db.Model):
    __tablename__ = "TestResult"
    id = db.Column(db.BigInteger, primary_key= True, autoincrement= True, nullable= False)
    tid = db.Column(db.BigInteger, db.ForeignKey('TestCase.id'), nullable= False)
    sid = db.Column(db.BigInteger, db.ForeignKey('UserSolution.id'), nullable= False)
    scoredAt = db.Column(db.Integer, nullable=False)
    result = db.Column(db.String, nullable= False)

    def __init__(self, id, tid, sid, result, scoredAt):
        self.id = id
        self.tid = tid
        self.sid = sid
        self.result = result
        self.scoredAt = scoredAt

class UserSolution(db.Model):
    __tablename__ = "UserSolution"
    id = db.Column(db.BigInteger, primary_key=True, autoincrement= True, nullable= False)
    uid = db.Column(db.BigInteger, db.ForeignKey('User.id'), nullable= False)
    pid = db.Column(db.BigInteger, db.ForeignKey('Problem.id'), nullable= False)
    createdAt = db.Column(db.Integer, nullable= False)
    updatedAt = db.Column(db.Integer)
    submittedAt = db.Column(db.Integer)
    sourceCode = db.Column(db.String)
    xml = db.Column(db.String)

    testResult = db.relationship('TestResult', backref='UserSolution', cascade='all, delete, delete-orphan')

    def __init__(self, id, uid, pid, createdAt, updatedAt, submittedAt, xml):
        self.id = id
        self.uid = uid
        self.pid = pid
        self.createdAt = createdAt
        self.updatedAt = updatedAt
        self.submittedAt = submittedAt
        self.xml = xml


@app.route('/problems', methods=['GET', 'OPTIONS'])
def view_problems():
    category = request.args.get('category')
    # query parameter category에 정수값이 지정될 때
    if category:
        queryByCategory = Problem.query.filter(Problem.category == category)
        problemByCategory = pd.read_sql(queryByCategory.statement, queryByCategory.session.bind)
        print(queryByCategory.all())
        print(json.loads(problemByCategory.to_json(orient='records')))
        return jsonify(data = json.loads(problemByCategory.to_json(orient='records')))
    else:
        # 모든 problem 불러오기
        queryInAll = Problem.query.filter(Problem.pid > 0)
        problemInAll = pd.read_sql(queryInAll.statement, queryInAll.session.bind)
        return jsonify(data = json.loads(problemInAll.to_json(orient='records')))


@app.route('/problems/<pid>', methods=['GET', 'OPTIONS'])
def view_each_problem(pid=''):
    tc = []
    problemQuery = Problem.query.filter(Problem.id == pid)
    if problemQuery.count():
        problemByPid = pd.read_sql(problemQuery.statement, problemQuery.session.bind)
        problem = json.loads(problemByPid.to_json(orient='records'))

        exampleQuery = Example.query.filter(Example.pid == int(pid))
        exampleByPid = pd.read_sql(exampleQuery.statement, exampleQuery.session.bind)
        examples = json.loads(exampleByPid.to_json(orient='records'))
        print(examples)
        for item in examples:
            print(item)
            if item['pid'] == int(pid):
                tmp = item.copy()
                del tmp['id']
                del tmp['pid']
                tc.append(tmp)
            else:
                break
        problem[0]["examples"] = tc
        return jsonify(data = problem[0], result = True)
    else :
        return jsonify(result = False, err_msg = "Not found")

#임시저장
int_pid = 1000

app.aid_count = 1
app.svsol = [{'pid': 1001, 'uid': 1, 'savedAt': 1570805217, 'savedXML':'<xml><block type="text_print" x="30" y="90"><value name="TEXT"><block type="text"><field name="TEXT">abc</field></block></value></block></xml>'},
                {'pid': 1002, 'uid': 1, 'savedAt': 1570805217, 'savedXML':'<xml></xml>'},
                  {'pid': 1003, 'uid': 1, 'savedAt': 1570805217, 'savedXML':'<xml></xml>'}]

def on_json_loading_failed_return_dict(e):
    return jsonify(result = False)

app.usersol_id = 1;
@app.route('/save', methods=['POST', 'GET'])
def save_sol():
    if request.method == 'POST':
        request.on_json_loading_failed = on_json_loading_failed_return_dict
        postedSol = request.get_json(force=True)
        tempSol = postedSol.copy()

        try:
            userSol = UserSolution.query.filter(UserSolution.pid==postedSol['pid'] and UserSolution.submittedAt == None).first()

            # 한번 저장된 solution일 때
            if userSol != None:
                userSol.updatedAt = postedSol['postedAt']
                userSol.xml = postedSol['xml']

                db.session.commit()
                return jsonify(result = True, msg="Successful to save solution.")
            # 한번도 저장된 solution이 아닐 때
            else :
                userSol = UserSolution(app.usersol_id, postedSol['uid'], postedSol['pid'], postedSol['postedAt'], None, None, postedSol['xml'])
                app.usersol_id += 1
                db.session.add(userSol)
                db.session.commit()
                return jsonify(result = True, msg="Successful to create solution.")
        except:
            return jsonify(result=False, err_msg="Check your key")

    elif request.method == 'GET':
        uid = int(request.args.get('uid'))
        pid = int(request.args.get('pid'))
        userSolQuery = UserSolution.query.filter(UserSolution.pid == pid and UserSolution.id == uid)
        userSolByPid = pd.read_sql(userSolQuery.statement, userSolQuery.session.bind)
        userSols = json.loads(userSolByPid.to_json(orient='records'))

        # 한번 저장된 solution일 때
        if len(userSols) != 0:
            return jsonify(data = userSols, result = True)
        else:
            return jsonify(result=False, err_msg="Not found")

#제출-post
# mysub = {'pid': 1000, 'subAt': 1570827639, 'subXML': '<init></init>', 'sourceCode': 'A, B = map(int,input().split())\nprint(A+B)'}
app.sid_count = 4
# app.subsol = [{'pid': 1001,'subAt': 1570705217, 'subXML':'<init></init>', 'sourceCode': 'A, B = map(int,input().split())\nprint(A+B)'},
#               {'pid': 1001,'subAt': 1570805217, 'subXML':'<init></init>', 'sourceCode': 'A, B = map(int,input().split())\nprint(A-B)'},
#                 {'pid': 1002,'subAt': 1570605217, 'subXML':'<init></init>', 'sourceCode': 'A, B = map(int,input().split())\nprint(A+B)'}]
app.subsol = [{'sid': 1, 'pid': 1004, 'uid': 1, 'title': '최대자리곱', 'category': '카테고리3', 'creator': '강하민', 'subXML': '<xml></xml>', 'source': ''},
            {'sid': 2, 'pid': 1004,'uid': 1, 'title': '최대자리곱', 'category': '카테고리3', 'creator': '강하민', 'subXML': '<xml></xml>', 'source': ''},
            {'sid': 3, 'pid':1001, 'uid': 1, 'title': 'A-B', 'category': '카테고리1', 'creator': '기쁜 국수', 'subXML': '<xml></xml>', 'source': ''},
            {'sid': 4, 'pid': 1000, 'uid': 1, 'title': 'A+B', 'category': '카테고리1', 'creator': '기쁜 국수', 'subXML': '<xml></xml>', 'source': ''}]
testresult = [{'sid': 1, 'tid': 30, 'result': '성공'},
              {'sid': 1, 'tid': 31, 'result': '성공'},
              {'sid': 1, 'tid': 32, 'result': '성공'},
              {'sid': 1, 'tid': 33, 'result': '성공'},
              {'sid': 1, 'tid': 34, 'result': '성공'},
              {'sid': 1, 'tid': 35, 'result': '성공'},
              {'sid': 1, 'tid': 36, 'result': '성공'},
              {'sid': 1, 'tid': 37, 'result': '성공'},
              {'sid': 1, 'tid': 38, 'result': '성공'},
              {'sid': 1, 'tid': 39, 'result': '실패'},
              {'sid': 2, 'tid': 30, 'result': '성공'},
              {'sid': 2, 'tid': 31, 'result': '성공'},
              {'sid': 2, 'tid': 32, 'result': '성공'},
              {'sid': 2, 'tid': 33, 'result': '성공'},
              {'sid': 2, 'tid': 34, 'result': '성공'},
              {'sid': 2, 'tid': 35, 'result': '성공'},
              {'sid': 2, 'tid': 36, 'result': '성공'},
              {'sid': 2, 'tid': 37, 'result': '성공'},
              {'sid': 2, 'tid': 38, 'result': '성공'},
              {'sid': 2, 'tid': 39, 'result': '성공'},
              {'sid': 3, 'tid': 6, 'result': '성공'},
              {'sid': 3, 'tid': 7, 'result': '성공'},
              {'sid': 3, 'tid': 8, 'result': '성공'},
              {'sid': 3, 'tid': 9, 'result': '성공'},
              {'sid': 3, 'tid': 10, 'result': '성공'},
              {'sid': 4, 'tid': 1, 'result': '성공'},
              {'sid': 4, 'tid': 2, 'result': '성공'},
              {'sid': 4, 'tid': 3, 'result': '성공'},
              {'sid': 4, 'tid': 4, 'result': '성공'},
              {'sid': 4, 'tid': 5, 'result': '실패'}
              ]
@app.route('/submit', methods=['POST', 'GET'])
def sub_sol():
    sid = 5;
    if request.method == 'POST':
        request.on_json_loading_failed = on_json_loading_failed_return_dict
        mysub = request.get_json(force=True)
        mysub['sid'] = sid
        sid += 1
        print(mysub)
        try:
            app.subsol.append(mysub)
            # app.subsol = sorted(app.subsol, key=itemgetter('pid'))
            print(app.subsol)
            return jsonify(result=True, msg="Successful to submit solution.")
        except KeyError as e:
            return jsonify(result=False, err_msg="Check your key")

    if request.method == 'GET':
        sid = int(request.args.get('sid'))
        if sid in map(itemgetter('sid'), app.subsol):
            a = [dict for dict in app.subsol if dict["sid"] == sid]
            return jsonify(data=a[0], result=200)


@app.route('/status/<uid>', methods=['GET'])
def view_my_status(uid):
    usersub = []
    category = request.args.get('category')
    try:
        # query parameter category에 정수값이 지정될 때
        if category != None:
            for item in app.subsol:
                if item['uid'] == int(uid) and item['category'] == category:
                    usersub.append(item)
                    print(usersub)
            usersub = addTestResult(usersub)
        # query parameter가 없을 때
        else:
            for item in app.subsol:
                if item['uid'] == int(uid):
                    usersub.append(item)
            usersub = addTestResult(usersub)
        return jsonify(result=True, data=usersub)
    except:
        return jsonify(result=False, err_msg="Bad request")

def addTestResult(arr):
    tr = []
    for item in arr:
        tmpsid = item['sid']
        for result in testresult:
            if result['sid'] == tmpsid:
                tmp = result.copy()
                del tmp['sid']
                tr.append(tmp)
            else:
                break
        item["testresult"] = tr
    return arr


if __name__ == "__main__":
    app.run(host="127.0.0.1", port="5000", debug = True)

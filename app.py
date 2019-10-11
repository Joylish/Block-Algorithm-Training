# -*- coding: utf-8 -*-
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
    pid = db.Column(db.BigInteger(), primary_key=True)
    title = db.Column(db.String(), unique=True)
    createdAt = db.Column(db.BigInteger())
    creator = db.Column(db.String(256))
    category = db.Column(db.String(256))
    content = db.Column(db.String())
    inputDetail = db.Column(db.String())
    outputDetail = db.Column(db.String())
    numSub = db.Column(db.Integer())
    correctRate = db.Column(db.REAL())
    initXML = db.Column(db.String())
    example = db.Column(db.String())


    def __init__(self, pid, title, createdAt, creator,
                 category, content, inputDetail, outputDetail,
                 numSub, correctRate, initXML, example):
        self.pid = pid
        self.createdAt = createdAt
        self.creator = creator
        self.category = category
        self.title = title
        self.content = content
        self.inputDetail = inputDetail
        self.outputDetail = outputDetail
        self.numSub = numSub
        self.correctRate = correctRate
        self.initXML = initXML
        self.example = example

class SavedSolution(db.model):
    __tablename__: "SavedSolution"
    pid = db.Column(db.BigInteger())
    uid = db.Column(db.BigInteger())
    savedAt = db.Column(db.String())
    savedXml = db.Column(db.text())
    def __init__(self, pid, uid, savedAt, savedXML):
        self.pid = pid
        self.uid = uid
        self.savedAt = savedAt
        self.savedXML = savedXML

class SubSolution(db.model):
    __tablename__: "SubSolution"
    sid = db.column(db.BigInteger(), primary_key =True)
    pid = db.column(db.BigInteger())
    uid = db.column(db.BigInteger())
    subAt = db.column(db.String())
    subXML = db.column(db.String())
    sourceCode = db.column(db.String())
    def __init__(self, sid, pid, uid, subAt, subXML, sourceCode):
        self.sid = sid
        self.pid = pid
        self.uid = uid
        self.savedAt = subAt
        self.subXML = subXML
        self.sourceCode =sourceCode

class Testcase(db.model):
    __tablename__: "Testcase"
    tid = db.column(db.BigInteger(), primary_key=True)
    pid = db.column(db.BigInteger())
    input = db.column(db.String())
    output = db.column(db.String())
    def __init__(self, tid, pid, input, output):
        self.tid = tid
        self.pid = pid
        self.input = input
        self.output = output

class Testresult(db.model):
    __tablename__: "Testresult"
    rid = db.column(db.BigInteger(), primary_key=True)
    tid = db.column(db.BigInteger())
    sid = db.column(db.BigInteger())
    result = db.column(db.String())

    def __init__(self, rid, tid, sid, result):
        self.rid = rid
        self.tid = tid
        self.sid = sid
        self.result = result

# 메인화면
@app.route('/')
def hello_world():
    return jsonify(greeting = '')

@app.route('/problems', methods=['GET', 'OPTIONS'])
def view_problems():
    category = request.args.get('category')
    # query parameter category에 정수값이 지정될 때
    if category:
        queryByCategory = Problem.query.filter(Problem.category == category)
        problemByCategory = pd.read_sql(queryByCategory.statement, queryByCategory.session.bind)
        return jsonify(data = json.loads(problemByCategory.to_json(orient='records')))
    else:
        # 모든 problem 불러오기
        queryInAll = Problem.query.filter(Problem.pid > 0)
        problemInAll = pd.read_sql(queryInAll.statement, queryInAll.session.bind)
        return jsonify(data = json.loads(problemInAll.to_json(orient='records')))

@app.route('/problems/<pid>', methods=['GET', 'OPTIONS'])
def view_each_problem(pid=''):
    queryByPid = Problem.query.filter(Problem.pid == pid)
    if queryByPid.count():
        problemByPid = pd.read_sql(queryByPid.statement,queryByPid.session.bind)
        return jsonify( data = json.loads(problemByPid.to_json(orient='records')),result = 200)
    else :
        return jsonify(result = 404, err_msg = "Not found")

#임시저장
mysav ={{'pid': '1004','title': '괄호의 값', 'category': '카테고리2', 'creator': '강하민', 'correctRate': '0.521',
       'numSub': '156', 'subXML': '<init></init>'}}



#제출-post
psub = {'pid': '1000', 'subAt': '', 'subXML': '<init></init>', 'sourceCode': 'A, B = map(int,input().split())\nprint(A+B)'}
app.sid_count = 1
app.submit = {}

@app.route('/submit', methods=['POST'])
def post_my_submit(pid=''):
        #request.on_json_loading_failed = on_json_loading_failed_return_dict
        #mysub = request.get_json(silent=True)
        psub["sid"] = app.sid_count
        app.submit[app.sid_count] = psub
        app.sid_count += 1

#제출상태-get
#상태에 따라
#1)시도-get
#2)해결-get
subdata = [{'pid': '1004','title': '최대자리곱', 'category': '카테고리1', 'creator': '강하민', 'correctRate': '0.521',
       'numSub': '156', 'saveXML': '<init></init>', 'finalstate': '제출완료'},{'pid': '1005','title': '트리의 아름다움', 'category': '카테고리3',
        'creator': 'newstein', 'correctRate': '0.521','numSub': '156' , 'saveXML': '<init></init>', 'finalstate': '제출완료'},
        {'pid':'1001', '문제이름': 'A-B', '카테고리': '카테고리1', '만든이': '기쁜 국수', '정답률': '0.521',
       'numSub': '156', 'subXML': '<init></init>', 'finalstate': '제출성공'},{'pid': '1000', '문제이름': 'A+B', '카테고리': '카테고리1',
        '만든이': '기쁜 국수', '정답률': '0.521', 'numSub': '156', 'saveXML': '<init></init>', 'finalstate': '제출성공'}]

@app.route('/status', methods=['GET'])
def view_my_status():
    # queryByPid = Problem.query.filter(Submit.pid == pid)
    #if queryByPid.count():
    if subdata != None:
            #submitByPid = Problem.query.filter(Submit.pid == pid)
            #submitByPid = pd.read_sql(queryByPid.statement, queryByPid.session.bind)
        return jsonify(data=json.loads(subdata.to_json(orient='records')), result=200)
    else:
        return jsonify(result=404, err_msg="Not found")

def on_json_loading_failed_return_dict(e):
    return {}
if __name__ == '__main__':
    app.run(debug=True)

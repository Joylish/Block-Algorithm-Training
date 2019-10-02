# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify, url_for
import json
from flask_sqlalchemy import SQLAlchemy
import pandas as pd

app = Flask(__name__)
app.config['SECRET_KEY'] = 'this is secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///BlockSolve.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Problem(db.Model):
    __tablename__ = "Problem"
    pid = db.Column(db.BigInteger(), primary_key=True)
    title = db.Column(db.String(), unique=True)
    createdAt = db.Column(db.String())
    creator = db.Column(db.String(256))
    # category는 index번호로 표시한다( 1: basic 2: stack ..)
    category =  db.Column(db.Integer())
    content = db.Column(db.String())
    inputDetail = db.Column(db.String())
    outputDetail = db.Column(db.String())
    numSubmission = db.Column(db.Integer())
    correctRate = db.Column(db.REAL())
    initXML = db.Column(db.String())

    def __init__(self, pid, title, createdAt, creator,
                 category, content, inputDetail, outputDetail,
                 numSubmission, correctRate, initXML):
        self.pid = pid
        self.createdAt = createdAt
        self.creator = creator
        self.category = category
        self.title = title
        self.content = content
        self.inputDetail = inputDetail
        self.outputDetail = outputDetail
        self.numSubmission = numSubmission
        self.correctRate = correctRate
        self.initXML = initXML

# class Save(db.model):
#     __tablename__: "Save"
#     sid = db.Column(db.BigInteger(), primary_key= True)
#     pid = db.Column(db.BigInteger())
#     uid = db.Column(db.BigInteger())
#     savedXml = db.Column(db.text())
#     savedAt = db.Column(db.String())
#
# class Submission(db.model):
#     __tablename__: "Submission"
#     sid = db.column(db.BigInteger(), primary_key =True)
#     pid = db.column(db.BigInteger())
#     uid = db.column(db.BigInteger())
#     submittedAt = db.column(db.String())
#     sourceCode = db.column(db.String())
#
# class Testcase(db.model):
#     __tablename__: "Testcase"
#     tid = db.column(db.BigInteger(), primary_key=True)
#     pid = db.column(db.BigInteger())
#     input = db.column(db.String())
#     output = db.column(db.String())
#
# class Testresult(db.model):
#     __tablename__: "Testresult"
#     rid = db.column(db.BigInteger(), primary_key=True)
#     sid = db.column(db.BigInteger())
#     result = db.column(db.Integer())
# 메인화면
@app.route('/')
def hello_world():
    return jsonify(greeting = '')

@app.route('/problems', methods=['GET'])
def view_problems(category=''):
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

@app.route('/problems/<pid>', methods=['GET'])
def view_each_problem(pid=''):
    queryByPid = Problem.query.filter(Problem.pid == pid)
    if queryByPid.count():
        problemByPid = pd.read_sql(queryByPid.statement,queryByPid.session.bind)
        return jsonify( data = json.loads(problemByPid.to_json(orient='records')),result = 200)
    else :
        return jsonify(result = 404, err_msg = "Not found")
if __name__ == '__main__':
    app.run(debug=True)

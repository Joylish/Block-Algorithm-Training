# -*- coding: utf-8 -*-
import time
from flask import Flask, request, jsonify
import json

from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import sys

app = Flask(__name__)
cors = CORS(app)

app.config['SECRET_KEY'] = 'this is secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///BlockSolve.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Problem(db.Model):
    __tablename__ = "Problem"
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True, nullable=False)
    title = db.Column(db.String, nullable=False)
    createdAt = db.Column(db.Integer, nullable=False)
    creator = db.Column(db.String(256), nullable=False)
    category = db.Column(db.String(256))
    content = db.Column(db.Text, nullable=False)
    inputDetail = db.Column(db.Text, nullable=False)
    outputDetail = db.Column(db.Text, nullable=False)
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

    def to_json(self):
        json = {
            'id': self.id,
            'title': self.title,
            'createdAt': self.createdAt,
            'creator': self.creator,
            'category': self.category,
            'content': self.content,
            'inputDetail': self.inputDetail,
            'outputDetail': self.outputDetail,
            'numSub': self.correctRate,
            'correctRate': self.correctRate,
            'initXML': self.initXML
        }
        return json


class Example(db.Model):
    __tablename__ = "Example"
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True, nullable=False)
    pid = db.Column(db.ForeignKey('Problem.id'), nullable=False)
    input = db.Column(db.Text, nullable=False)
    output = db.Column(db.Text, nullable=False)

    def __init__(self, id, pid, input, output):
        self.id = id
        self.pid = pid
        self.input = input
        self.output = output


class User(db.Model):
    __tablename__ = "User"
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    createdAt = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String, nullable=False)

    userSolution = db.relationship('UserSolution', backref='User', cascade='all, delete, delete-orphan')

    def __init__(self, id, name, createdAt, email):
        self.id = id
        self.name = name
        self.createdAt = createdAt
        self.email = email


class TestCase(db.Model):
    __tablename__ = "TestCase"
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True, nullable=False)
    pid = db.Column(db.BigInteger, db.ForeignKey('Problem.id'), nullable=False)
    input = db.Column(db.Text, nullable=False)
    output = db.Column(db.Text, nullable=False)

    testResult = db.relationship('TestResult', backref='TestCase', cascade='all, delete, delete-orphan')

    def __init__(self, id, pid, input, output):
        self.id = id
        self.pid = pid
        self.input = input
        self.output = output


class TestResult(db.Model):
    __tablename__ = "TestResult"
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True, nullable=False)
    tid = db.Column(db.BigInteger, db.ForeignKey('TestCase.id'), nullable=False)
    sid = db.Column(db.BigInteger, db.ForeignKey('UserSolution.id'), nullable=False)
    scoredAt = db.Column(db.Integer, nullable=False)
    result = db.Column(db.String, nullable=False)

    def __init__(self, id, sid, tid, scoredAt, result):
        self.id = id
        self.tid = tid
        self.sid = sid
        self.result = result
        self.scoredAt = scoredAt

    def to_json(self):
        json = {
            'id': self.id,
            'tid': self.tid,
            'sid': self.sid,
            'user_output': self.result,
            'scoredAt': self.scoredAt
        }
        return json


class UserSolution(db.Model):
    __tablename__ = "UserSolution"
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True, nullable=False)
    uid = db.Column(db.BigInteger, db.ForeignKey('User.id'), nullable=False)
    pid = db.Column(db.BigInteger, db.ForeignKey('Problem.id'), nullable=False)
    createdAt = db.Column(db.Integer, nullable=False)
    updatedAt = db.Column(db.Integer)
    submittedAt = db.Column(db.Integer)
    sourceCode = db.Column(db.String)
    xml = db.Column(db.String)
    accept = db.Column(db.Boolean)

    testResult = db.relationship('TestResult', backref='UserSolution', cascade='all, delete, delete-orphan')

    def __init__(self, id, uid, pid, createdAt, updatedAt, submittedAt, xml, sourceCode, accept):
        self.id = id
        self.uid = uid
        self.pid = pid
        self.createdAt = createdAt
        self.updatedAt = updatedAt
        self.submittedAt = submittedAt
        self.xml = xml
        self.sourceCode = sourceCode
        self.accept = accept

    def to_json(self):
        json = {
            'id': self.id,
            'uid': self.uid,
            'pid': self.pid,
            'createdAt': self.createdAt,
            'updatedAt': self.updatedAt,
            'submittedAt': self.submittedAt,
            'xml': self.xml,
            'sourceCode': self.sourceCode,
            'accept': self.accept
        }
        return json


@app.route('/problems', methods=['GET'])
def view_problems():
    per_page = 10
    page = request.args.get('page')
    category = request.args.get('category')
    # query parameter category에 정수값이 지정될 때
    try:
        if page:
            if category:
                queryByCategory = Problem.query.filter(Problem.category == category).order_by(
                    Problem.createdAt.asc()).paginate(int(page), per_page, error_out=False).items
                problemsByCategory = []
                for i in queryByCategory:
                    problemsByCategory.append(i.to_json())
                return jsonify(data=problemsByCategory, result=True)
            else:
                # 모든 problem 불러오기
                queryInAll = Problem.query.order_by(Problem.createdAt.asc()).paginate(int(page), per_page,
                                                                                      error_out=False).items
                problemsInAll = []
                for i in queryInAll:
                    problemsInAll.append(i.to_json())
                return jsonify(data=problemsInAll, result=True)
        else:
            if category:
                queryByCategory = Problem.query.filter(Problem.category == category)
                problemsBindByCategory = pd.read_sql(queryByCategory.statement, queryByCategory.session.bind)
                problemsByCategory = json.loads(problemsBindByCategory.to_json(orient='records'))
                return jsonify(data=problemsByCategory, result=True)
            else:
                # 모든 problem 불러오기
                queryInAll = Problem.query.filter(Problem.id > 0)
                problemsBindInAll = pd.read_sql(queryInAll.statement, queryInAll.session.bind)
                problemsInAll = json.loads(problemsBindInAll.to_json(orient='records'))
                return jsonify(data=problemsInAll, result=True)
    except Exception as e:
        print(e.message)
        return jsonify(result=False, error=e.message)


@app.route('/problems/<pid>', methods=['GET'])
def view_each_problem(pid=''):
    tc = []
    problemQuery = Problem.query.filter(Problem.id == pid)
    try:
        if problemQuery.count():
            problemByPid = pd.read_sql(problemQuery.statement, problemQuery.session.bind)
            problem = json.loads(problemByPid.to_json(orient='records'))

            exampleQuery = Example.query.filter(Example.pid == int(pid))
            exampleByPid = pd.read_sql(exampleQuery.statement, exampleQuery.session.bind)
            examples = json.loads(exampleByPid.to_json(orient='records'))

            for item in examples:
                if item['pid'] == int(pid):
                    tmp = item.copy()
                    del tmp['id']
                    del tmp['pid']
                    tc.append(tmp)
                else:
                    break
            problem[0]["examples"] = tc
            return jsonify(data=problem[0], result=True)
        else:
            return jsonify(result=False, error="Not found")
    except Exception as e:
        print(e.message)
        return jsonify(result=False, error=e.message)


# 임시저장
def on_json_loading_failed_return_dict(e):
    return jsonify(result=False)


@app.route('/save', methods=['POST', 'GET'])
def save_sol():
    if request.method == 'POST':
        request.on_json_loading_failed = on_json_loading_failed_return_dict
        postedSol = request.get_json(force=True)
        UserSolutionForBigID = UserSolution.query.order_by(UserSolution.id.desc()).first()
        if UserSolutionForBigID:
            usersol_id = int(UserSolutionForBigID.id)
        else:
            usersol_id = 1
        try:
            userSol = UserSolution.query.filter(
                UserSolution.pid == postedSol['pid'] and UserSolution.submittedAt.is_(None)).first()

            # 한번 저장된 solution일 때
            if userSol != None:
                userSol.updatedAt = postedSol['postedAt']
                userSol.xml = postedSol['xml']
                db.session.commit()
                return jsonify(UserSolutionID=usersol_id, result=True, msg="Successful to save solution.")

            # 한번도 저장된 solution이 아닐 때
            else:
                usersol_id += 1
                userSol = UserSolution(usersol_id, postedSol['uid'], postedSol['pid'], postedSol['postedAt'], None,
                                       None, postedSol['xml'], None, None)
                db.session.add(userSol)
                db.session.commit()
                return jsonify(UserSolutionID=usersol_id, result=True, msg="Successful to create solution.")
        except Exception as e:
            return jsonify(result=False, error=e.message)

    elif request.method == 'GET':
        uid = int(request.args.get('uid'))
        pid = int(request.args.get('pid'))
        userSolQuery = UserSolution.query.filter(UserSolution.pid == pid and UserSolution.uid == uid).filter(
            UserSolution.submittedAt is None)
        userSolByPid = pd.read_sql(userSolQuery.statement, userSolQuery.session.bind)
        userSols = json.loads(userSolByPid.to_json(orient='records'))
        # 한번 저장된 solution일 때
        if len(userSols) != 0:
            return jsonify(sid=userSols[0]['id'], data=userSols, result=True)
        else:
            return jsonify(result=False, error="Not found. Check uid and pid.")


# 제출

def testAndverify(subSol, testresult_id):
    # id, uid, pid, createdAt, updatedAt, submittedAt, xml, sourceCode, accept
    pid = subSol.pid
    source = subSol.sourceCode
    testCase = TestCase.query.filter(TestCase.pid == pid).all()

    data = {}
    allresults = []
    accept = True
    try:
        for i in range(len(testCase)):

            out = open('./user_output/' + str(int(subSol.id) % 1000) + '.txt', 'w+')
            stdout = sys.stdout
            sys.stdout = out
            testCaseInput = testCase[i].input

            # testCode 만들고 실행
            testCode = testCaseInput + '\n' + source
            code = compile(testCode, '<string>', 'exec')
            exec(code)

            # 예상결과와 실제결과 비교
            output = testCase[i].output + '\n'
            result = False
            out.seek(0, 0)
            if out.read() == output:
                result = True
            else:
                accept = False

            testResult = TestResult(testresult_id, subSol.id, testCase[i].id, int(round(time.time() * 1000)), result)
            allresults.append(testResult.to_json())
            testresult_id += 1
            db.session.add(testResult)
            db.session.commit()
            out.close()
            sys.stdout = stdout
    except Exception as e:
        accept = False
        data['accept'] = accept
        data['error'] = e.message
        return data

    data['accept'] = accept
    data['result'] = allresults
    return data


@app.route('/submit', methods=['POST', 'GET'])
def submit_sol():
    if request.method == 'POST':
        request.on_json_loading_failed = on_json_loading_failed_return_dict
        postedSol = request.get_json(force=True)
        testResultByBig = TestResult.query.order_by(TestResult.id.desc()).first()
        UserSolutionForBigID = UserSolution.query.order_by(UserSolution.id.desc()).first()
        if testResultByBig:
            testresult_id = int(testResultByBig.id)
        else:
            testresult_id = 1;
        if UserSolutionForBigID:
            usersol_id = int(UserSolutionForBigID.id)
        else:
            usersol_id = 1

        try:
            subSol = UserSolution.query.filter(
                UserSolution.pid == postedSol['pid']).filter(UserSolution.submittedAt is None).first()
            # 한번 제출된 solution일 때
            if subSol is not None:
                subSol.submittedAt = postedSol['postedAt']
                subSol.xml = postedSol['xml']
                subSol.sourceCode = postedSol['sourceCode']
                db.session.commit()

            # 한번도 제출된 solution이 아닐 때
            else:
                # id, uid, pid, createdAt, updatedAt, submittedAt, xml, sourceCode, accept
                subSol = UserSolution(usersol_id, postedSol['uid'], postedSol['pid'], postedSol['postedAt'], None,
                                      postedSol['postedAt'], postedSol['xml'], postedSol['sourceCode'], None)
            result = testAndverify(subSol, testresult_id)
            if not result['accept']:
                subSol.accept = False
                db.session.commit()
                return jsonify(accept=result['accept'], error=result['error'])
            else:
                subSol.accept = result['accept']
                db.session.commit()
                return jsonify(result=result['result'], accept=result['accept'])
        except Exception as e:
            return jsonify(result=False, error=e.message)

    if request.method == 'GET':
        sid = int(request.args.get('sid'))
        try:
            userSolQuery = UserSolution.query.filter(UserSolution.id == sid)
            userSolByPid = pd.read_sql(userSolQuery.statement, userSolQuery.session.bind)
            userSols = json.loads(userSolByPid.to_json(orient='records'))
            if len(userSols) > 0:
                return jsonify(data=userSols, result=True)
        except Exception as e:
            return jsonify(result=False, error=e.message)


@app.route('/status/<uid>', methods=['GET'])
def view_my_status(uid=''):
    per_page = 10
    page = request.args.get('page')
    category = request.args.get('category')
    usersub = []
    try:
        # pagination 지정될 때
        if page:
            queryByPage = UserSolution.query.join(Problem). \
                with_entities(UserSolution.id, UserSolution.uid, UserSolution.pid,
                              UserSolution.createdAt, UserSolution.updatedAt,
                              UserSolution.submittedAt, UserSolution.xml,
                              UserSolution.sourceCode, UserSolution.accept,
                              Problem.category, Problem.title). \
                filter(UserSolution.pid == Problem.id).order_by(Problem.createdAt.asc()). \
                paginate(int(page), per_page, error_out=False).items
            cols = ['sid', 'uid', 'pid', 'createdAt', 'updatedAt', 'submittedAt', 'xml',
                    'sourceCode', 'accept', 'category', 'title']
            problemsByPage = []
            for i in queryByPage:
                cnt = 0
                jsonn = {}
                for col in cols:
                    jsonn[col] = i[cnt]
                    cnt += 1
                problemsByPage.append(jsonn)

            for item in problemsByPage:
                item['testResult'] = []
                testResultQuery = TestResult.query.filter(TestResult.sid == int(item['sid']))
                testResultBySid = pd.read_sql(testResultQuery.statement, testResultQuery.session.bind)
                item['testResult'] = json.loads(testResultBySid.to_json(orient='records'))


        # pagination 지정되지 않을때
        else:
            queryByPa = UserSolution.query.join(Problem). \
                with_entities(UserSolution.id, UserSolution.uid, UserSolution.pid,
                              UserSolution.createdAt, UserSolution.updatedAt,
                              UserSolution.submittedAt, UserSolution.xml,
                              UserSolution.sourceCode, UserSolution.accept,
                              Problem.category, Problem.title). \
                filter(UserSolution.pid == Problem.id).order_by(Problem.createdAt.asc())
            queryByPag = pd.read_sql(queryByPa.statement, queryByPa.session.bind)
            queryByPage = json.loads(queryByPag.to_json(orient='records'))
            problemsByPage = []

            for i in queryByPage:
                problemsByPage.append(i)
            for item in problemsByPage:
                item['testResult'] = []
                testResultQuery = TestResult.query.filter(TestResult.sid == int(item['id']))
                testResultBySid = pd.read_sql(testResultQuery.statement, testResultQuery.session.bind)
                item['testResult'] = json.loads(testResultBySid.to_json(orient='records'))

        # query parameter category에 정수값이 지정될 때
        if category:
            for item in problemsByPage:
                if item['uid'] == int(uid) and item['category'] == category:
                    usersub.append(item)
        # query parameter가 없을 때
        else:
            for item in problemsByPage:
                if item['uid'] == int(uid):
                    usersub.append(item)
        return jsonify(result=True, data=usersub)
    except Exception as e:
        print(e.message)
        return jsonify(result=False, error=e.message)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port="5000", debug=True)

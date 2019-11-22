import json
from operator import itemgetter

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import pandas as pd

app = Flask(__name__)
cors = CORS(app)

app.config['SECRET_KEY'] = 'this is secret'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blocksolve:blocklysolve0130@202.30.31.251/blocksolve'



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


    def __init__(self, pid, title, createdAt, creator,
                 category, content, inputDetail, outputDetail,
                 numSub, correctRate, initXML):
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

testcase =   [
              {'tid': 1, 'pid': 1000, 'input': 'a=2\nb=3', 'output': '5'},
              {'tid': 2, 'pid': 1000, 'input': 'a=3\nb=5', 'output': '8'},
              {'tid': 3, 'pid': 1000, 'input': 'a=7\nb=9', 'output': '16'},
              {'tid': 4, 'pid': 1000, 'input': 'a=3\nb=2', 'output': '1'},
              {'tid': 5, 'pid': 1001, 'input': 'a=5\nb=3', 'output': '2'},
              {'tid': 6, 'pid': 1001, 'input': 'a=7\nb=2', 'output': '5'},
              {'tid': 7, 'pid': 1002, 'input': '(()[[]])([])', 'output': '28'}
              ]

@app.route('/problems/<pid>', methods=['GET', 'OPTIONS'])
def view_each_problem(pid=''):
    int_pid = int(pid)
    tc = []
    tcCnt = 0
    queryByPid = Problem.query.filter(Problem.pid == pid)
    if queryByPid.count():
        problemByPid = pd.read_sql(queryByPid.statement,queryByPid.session.bind)
        data = json.loads(problemByPid.to_json(orient='records'))
        for item in testcase:
            if item['pid'] == int_pid:
                if tcCnt < 3:
                    tcCnt += 1
                    tmp = item.copy()
                    del tmp['tid']
                    del tmp['pid']
                    tc.append(tmp)
                else:
                    break
        data[0]["example"] = tc
        return jsonify(data = data[0], result = True)
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

@app.route('/save', methods=['POST', 'GET'])
def save_sol():
    if request.method == 'POST':
        request.on_json_loading_failed = on_json_loading_failed_return_dict
        mysav = request.get_json(force=True)
        #queryByPid = SavedSol.query.filter(Problem.pid == pid)
        # if uid in map(itemgetter('uid'), app.svsol) and pid in map(itemgetter('pid'), app.svsol):
        try:
            # 한번 저장된 solution일 때
            if mysav['pid'] in map(itemgetter('pid'), app.svsol):
                cidx = [i for i,_ in enumerate(app.svsol) if _['pid'] == mysav['pid']][0]
                app.svsol[cidx] = mysav
                app.svsol = sorted(app.svsol, key=itemgetter('pid'))
                return jsonify(result = True, msg="Successful to save solution.")

            # 한번도 저장된 solution이 아닐 때
            else:
                # if queryByPid.count():
                app.svsol.append(mysav)
                app.svsol = sorted(app.svsol, key=itemgetter('pid'))
                print(app.svsol)
                return jsonify(result = True, msg="Successful to create solution.")
        except:
            return jsonify(result=False, err_msg="Check your key")

    elif request.method == 'GET':
        uid = int(request.args.get('uid'))
        pid = int(request.args.get('pid'))
        if uid in map(itemgetter('uid'), app.svsol) and pid in map(itemgetter('pid'), app.svsol):
            # problemByPid = pd.read_sql(queryByPid.statement, queryByPid.session.bind)
            # return jsonify(data=json.loads(problemByPid.to_json(orient='records')), result=200)
            a = [dict for dict in app.svsol if dict["pid"] == pid and dict["uid"] == uid]
            return jsonify(data = a[0], result = True)
        else:
            return jsonify(result=False, err_msg="Not found")

#제출-post
app.sid_count = 4
app.subsol = [{'sid': 1, 'pid': 1004, 'uid': 1, 'subAt': 1580505217, 'title': '최대자리곱', 'category': '카테고리3', 'creator': '강하민', 'subXML': '<xml></xml>', 'source': ''},
            {'sid': 2, 'pid': 1004,'uid': 1, 'subAt': 1580405217, 'title': '최대자리곱', 'category': '카테고리3', 'creator': '강하민', 'subXML': '<xml></xml>', 'source': ''},
            {'sid': 3, 'pid':1001, 'uid': 1, 'subAt': 1580605217, 'title': 'A-B', 'category': '카테고리1', 'creator': '기쁜 국수', 'subXML': '<xml></xml>', 'source': ''},
            {'sid': 4, 'pid': 1000, 'uid': 1, 'subAt': 1580805217, 'title': 'A+B', 'category': '카테고리1', 'creator': '기쁜 국수', 'subXML': '<xml></xml>', 'source': ''}]
testresult = [{'sid': 1, 'tid': 30, 'result': True},
              {'sid': 1, 'tid': 31, 'result': True},
              {'sid': 1, 'tid': 32, 'result': True},
              {'sid': 1, 'tid': 33, 'result': True},
              {'sid': 1, 'tid': 34, 'result': True},
              {'sid': 1, 'tid': 35, 'result': True},
              {'sid': 1, 'tid': 36, 'result': True},
              {'sid': 1, 'tid': 37, 'result': True},
              {'sid': 1, 'tid': 38, 'result': True},
              {'sid': 1, 'tid': 39, 'result': False},
              {'sid': 2, 'tid': 30, 'result': True},
              {'sid': 2, 'tid': 31, 'result': True},
              {'sid': 2, 'tid': 32, 'result': True},
              {'sid': 2, 'tid': 33, 'result': True},
              {'sid': 2, 'tid': 34, 'result': True},
              {'sid': 2, 'tid': 35, 'result': True},
              {'sid': 2, 'tid': 36, 'result': True},
              {'sid': 2, 'tid': 37, 'result': True},
              {'sid': 2, 'tid': 38, 'result': True},
              {'sid': 2, 'tid': 39, 'result': True},
              {'sid': 3, 'tid': 6, 'result': True},
              {'sid': 3, 'tid': 7, 'result': True},
              {'sid': 3, 'tid': 8, 'result': True},
              {'sid': 3, 'tid': 9, 'result': True},
              {'sid': 3, 'tid': 10, 'result': True},
              {'sid': 4, 'tid': 1, 'result': True},
              {'sid': 4, 'tid': 2, 'result': True},
              {'sid': 4, 'tid': 3, 'result': True},
              {'sid': 4, 'tid': 4, 'result': True},
              {'sid': 4, 'tid': 5, 'result': False}
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
            return jsonify(result=True, sid=sid, msg="Successful to submit solution.")
        except KeyError as e:
            return jsonify(result=False, err_msg="Check your key")

    if request.method == 'GET':
        sid = int(request.args.get('sid'))
        if sid in map(itemgetter('sid'), app.subsol):
            a = [dict for dict in app.subsol if dict["sid"] == sid]
            return jsonify(data=a[0], result=True)


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
                    print(item)
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
        tmpsid = int(item['sid'])
        print(testresult)
        for result in testresult:
            print(result)
            if int(result['sid']) == int(tmpsid):
                tmp = result.copy()
                del tmp['sid']
                tr.append(tmp)
                print(tr)
            else:
                break
        # print(tr)
        item["testresult"] = tr
        # print(item)
    return arr


if __name__ == '__main__':
    app.run()

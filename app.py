from flask import Flask, render_template, jsonify, request, session, redirect, url_for

app = Flask(__name__)

from pymongo import MongoClient
import certifi

client = MongoClient('mongodb+srv://test:sparta@cluster0.ugilq.mongodb.net/myFirstDatabase?retryWrites=true&w=majority', tlsCAFile=certifi.where())
db = client.travel

# jwt 토큰을 만들 때 필요한 key
SECRET_KEY = 'SPARTA'

# jwt 패키지 사용
import jwt

# 토큰에 만료시간을 줘야하기 때문에, datetime 모듈도 사용합니다.
import datetime

# 회원가입 시 비밀번호를 암호화하여 DB에 저장
import hashlib




@app.route('/')
def home():
    return render_template('register.html')

@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)


@app.route('/register')
def register():
    return render_template('register.html')


#################################
##  로그인 회원가입을 위한 API     ##
#################################

# [회원가입 API]
# id, pw, nickname을 받아서, mongoDB에 저장.
# 저장하기 전에, pw를 sha256 방법(=단방향 암호화. 풀어볼 수 없음)으로 암호화해서 저장합니다.
@app.route('/api/sign_up/save', methods=['POST'])
def api_register():
    name_receive = request.form['name_give']
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']

    # id 중복 체크
    dup_id = db.users.find_one({'id': id_receive}, {'_id': False})
    if dup_id is not None:
        return jsonify({'result': 'fail', 'msg': '이미 사용중인 아이디입니다.'})

    # pw의 해쉬값
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()
    db.users.insert_one({'name': name_receive, 'id': id_receive, 'pw': pw_hash})

    return jsonify({'result': 'success', 'msg': '가입 성공!'})


@app.route('/api/sign_up/check_dup', methods=['GET'])
def api_check_dup():
    id_receive = request.args.get('id_give')

    dup_id = db.users.find_one({'id': id_receive}, {'_id': False})
    if dup_id is not None:
        return jsonify({'result': 'fail', 'msg': '이미 사용중인 아이디입니다.'})

    return jsonify({'result': 'success', 'msg': '멋진 아이디에요!'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)


from flask import Flask, render_template, jsonify, request, session, redirect, url_for, Blueprint, current_app
from pymongo import MongoClient
import certifi
# jwt 패키지 사용
import jwt
# 토큰에 만료시간을 줘야하기 때문에, datetime 모듈도 사용합니다.
import datetime
# 회원가입 시 비밀번호를 암호화하여 DB에 저장
import hashlib

blue_login = Blueprint('login', __name__, url_prefix='/api')

client = MongoClient('mongodb+srv://test:sparta@cluster0.ugilq.mongodb.net/myFirstDatabase?retryWrites=true&w=majority',
                     tlsCAFile=certifi.where())
db = client.travel


# [회원가입 API]
# name, id, pw을 받아서, mongoDB에 저장.
# 저장하기 전에, pw를 sha256 방법(=단방향 암호화. 풀어볼 수 없음)으로 암호화해서 저장합니다.
@blue_login.route('/sign_up/save', methods=['POST'])
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


# [회원가입 아이디 중복체크 API]
# id 받아서 DB에 값이 있는지 체크
@blue_login.route('/sign_up/check_dup', methods=['GET'])
def api_check_dup():
    id_receive = request.args.get('id_give')

    dup_id = db.users.find_one({'id': id_receive}, {'_id': False})
    if dup_id is not None:
        return jsonify({'result': 'fail', 'msg': '이미 사용중인 아이디입니다.'})

    return jsonify({'result': 'success', 'msg': '멋진 아이디에요!'})


# [로그인 API]
# id, pw를 받아서 맞춰보고, 토큰을 만들어 발급.
@blue_login.route('/sign_in', methods=['POST'])
def api_login():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']

    # 회원가입 때와 같은 방법으로 pw를 암호화.
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    # id, 암호화된pw을 가지고 해당 유저를 찾기.
    result = db.users.find_one({'id': id_receive, 'pw': pw_hash})

    # 찾으면 JWT 토큰을 만들어 발급합니다.
    if result is not None:
        # JWT 토큰에는, payload와 시크릿키가 필요하다.
        # 시크릿키가 있어야 토큰을 디코딩(=풀기) 해서 payload 값을 볼 수 있다.
        # 아래에선 id와 exp를 담았다. 즉, JWT 토큰을 풀면 유저ID 값을 알 수 있다.
        # exp에는 만료시간을 넣어준다. 만료시간이 지나면, 시크릿키로 토큰을 풀 때 만료되었다고 에러가 난다.

        # refreshToken 생성 및 DB저장
        payload = {
            'id': id_receive,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=current_app.config['REFRESHTOKENVALIDTIME'])
        }
        refreshToken = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
        db.users.update_one({'id': id_receive}, {'$set': {current_app.config['REFRESHTOKEN']: refreshToken}})

        # accessToken 생성
        payload = {
            'id': id_receive,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=current_app.config['ACCESSTOKENVALIDTIME'])
        }
        accessToken = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')

        # token을 반환.
        return jsonify(
            {'result': 'success', current_app.config['ACCESSTOKEN']: accessToken,
             current_app.config['REFRESHTOKEN']: refreshToken})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})

from flask import Flask, render_template, jsonify, request, session, redirect, url_for, make_response
from pymongo import MongoClient
import certifi
import math
# jwt 패키지 사용
import jwt
# 토큰에 만료시간을 줘야하기 때문에, datetime 모듈도 사용합니다.
import datetime
# 회원가입 시 비밀번호를 암호화하여 DB에 저장
import hashlib
# decorator jwt 검사를 위한 미들웨어로 활용
from functools import wraps

app = Flask(__name__)
# config 파일 참조
app.config.from_pyfile('config.py')

client = MongoClient(app.config['MONGODB'], tlsCAFile=certifi.where())
db = client.travel


#################################
##        토큰 검사 미들웨어      ##
#################################
def home_decorator():
    def _home_decorator(f):
        @wraps(f)
        def __home_decorator(*args, **kwargs):
            accessToken_receive = request.cookies.get(app.config['ACCESSTOKEN'])
            refreshToken_receive = request.cookies.get(app.config['REFRESHTOKEN'])

            # AccessToken이 유효한가? True or False
            isValidAccessToken = getAccessToken()

            # RefreshToken이 유효한가? True or False
            isValidRefreshToken = getRefreshToken()
            print('deco')
            if isValidAccessToken and isValidRefreshToken:
                print('1')
                # AccessToken과 RefreshToken 모두 유효 => 계속 진행
                result = f()
                return result

            elif isValidAccessToken is not True and isValidRefreshToken:
                print('2')
                # AccessToken 만료 RefreshToken 유효 => AccessToken 재발급
                old_payload = jwt.decode(refreshToken_receive, app.config['SECRET_KEY'], algorithms=['HS256'])
                payload = {
                    'id': old_payload['id'],
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=app.config['ACCESSTOKENVALIDTIME'])
                }
                accessToken = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

                result = make_response(f())
                result.set_cookie("accessToken", accessToken)
                return result

            elif isValidAccessToken and isValidRefreshToken is not True:
                print('3')
                # AccessToken 유효 RefreshToken 만료 => RefreshToken 재발급
                old_payload = jwt.decode(accessToken_receive, app.config['SECRET_KEY'], algorithms=['HS256'])
                # refreshToken 생성 및 DB저장
                payload = {
                    'id': old_payload['id'],
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=app.config['REFRESHTOKENVALIDTIME'])
                }
                refreshToken = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

                db.users.update_one({'id': old_payload['id']}, {'$set': {app.config['REFRESHTOKEN']: refreshToken}})

                result = make_response(f())
                result.set_cookie("refreshToken", refreshToken)
                return result

            else:
                print('4')
                # AccessToken과 RefreshToken 모두 만료 => 로그인 페이지
                return redirect(url_for("login"))

        return __home_decorator

    return _home_decorator


def getAccessToken():
    accessToken_receive = request.cookies.get(app.config['ACCESSTOKEN'])
    try:
        jwt.decode(accessToken_receive, app.config['SECRET_KEY'], algorithms=['HS256'])
        print('A 1')
        return True
    except jwt.ExpiredSignatureError:  # 유효기간 만료된 토큰 디코드 시
        print('A 2')
        return False
    except jwt.exceptions.DecodeError:  # 해당 token이 올바르게 디코딩되지 않았다면
        print('A 3')
        return False


def getRefreshToken():
    refreshToken_receive = request.cookies.get(app.config['REFRESHTOKEN'])
    try:
        payload = jwt.decode(refreshToken_receive, app.config['SECRET_KEY'], algorithms=['HS256'])

        # 유저 ID로 유저 DB SELECT
        user_info = db.users.find_one({"id": payload['id']})

        # 쿠키에 저장된 refreshToken와 DB에 저장된 refreshToken가 같은지 비교
        if refreshToken_receive == user_info[app.config['REFRESHTOKEN']]:
            print('R 1')
            return True
        else:
            print('R 2')
            return False
    except jwt.ExpiredSignatureError:  # 유효기간 만료된 토큰 디코드 시
        print('R 3')
        return False
    except jwt.exceptions.DecodeError:  # 해당 token이 올바르게 디코딩되지 않았다면
        print('R 4')
        return False


#################################
##           메인페이지           ##
#################################

# 메인페이지 Route
@app.route('/')
@home_decorator()
def home():
    token_receive = request.cookies.get(app.config['ACCESSTOKEN'])
    try:
        payload = jwt.decode(token_receive, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_info = db.users.find_one({"id": payload["id"]})
        return render_template('index.html', user=user_info)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return render_template('index.html', user=None)


# 메인페이지 API
@app.route('/api/plans', methods=['GET'])
def get_plans():
    location = request.args.get('location', "")
    query = request.args.get('query', "")
    sort = request.args.get('sort', "date")
    page = request.args.get('page', 1, type=int)
    limit = 12

    option = {}

    if len(location) > 0:
        option['location'] = location

    if len(query) > 0:
        option['location'] = query

    plans = list(db.plan.find(option).skip((page - 1) * limit).limit(limit).sort(sort, -1))

    results = []
    for document in plans:
        document['_id'] = str(document['_id'])
        results.append(document)

    total_count = db.plan.count_documents(option)
    last_page = math.ceil(total_count / limit)

    none = ""

    if total_count == 0:
        none = "원하시는 여행계획이 없습니다."

    return jsonify({'plans': results, 'last_page': last_page, 'page': page, 'none': none})


#################################
##        로그인 회원가입         ##
#################################

# 로그인 Route
@app.route('/login')
def login():
    return render_template('login.html')


# 회원가입 Route
@app.route('/register')
def register():
    return render_template('register.html')


# [회원가입 API]
# name, id, pw을 받아서, mongoDB에 저장.
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


# [회원가입 아이디 중복체크 API]
# id 받아서 DB에 값이 있는지 체크
@app.route('/api/sign_up/check_dup', methods=['GET'])
def api_check_dup():
    id_receive = request.args.get('id_give')

    dup_id = db.users.find_one({'id': id_receive}, {'_id': False})
    if dup_id is not None:
        return jsonify({'result': 'fail', 'msg': '이미 사용중인 아이디입니다.'})

    return jsonify({'result': 'success', 'msg': '멋진 아이디에요!'})


# [로그인 API]
# id, pw를 받아서 맞춰보고, 토큰을 만들어 발급.
@app.route('/api/sign_in', methods=['POST'])
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
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=app.config['REFRESHTOKENVALIDTIME'])
        }
        refreshToken = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
        db.users.update_one({'id': id_receive}, {'$set': {app.config['REFRESHTOKEN']: refreshToken}})

        # accessToken 생성
        payload = {
            'id': id_receive,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=app.config['ACCESSTOKENVALIDTIME'])
        }
        accessToken = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

        # token을 반환.
        return jsonify({'result': 'success', app.config['ACCESSTOKEN']: accessToken, app.config['REFRESHTOKEN']: refreshToken})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


#################################
        ##  PLANS  ##
#################################

# jinja test

@app.route('/result', methods=['POST', 'GET'])
def detailCardResult():
    if request.method == 'POST':
        result = request.form
        return render_template("card_detail_result.html", result=detailCardResult)


## HTML을 주는 부분
@app.route('/')
def plans():
    myname = "Sparta"
    return render_template('card.html', name=myname)



## API 역할을 하는 부분

@app.route('/plans', methods=['POST'])
def save_plans():
    sample_receive = request.form['sample_give']
    print(sample_receive)
    return jsonify({'msg': 'POST 요청 완료!'})


# 프로필 블루프린트 등록 (연결)
# app.register_blueprint(user.bp)


## local port
if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

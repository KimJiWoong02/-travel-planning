from flask import Flask, render_template, jsonify, request, session, redirect, url_for, make_response
from pymongo import MongoClient
import certifi
import math
# jwt 패키지 사용
import jwt
from bson import ObjectId
# 토큰에 만료시간을 줘야하기 때문에, datetime 모듈도 사용
import datetime
import user
from checkToken import getAccessToken, getRefreshToken
from login import blue_login

app = Flask(__name__)
# config 파일 참조
app.config.from_pyfile('config.py')

client = MongoClient('mongodb+srv://test:sparta@cluster0.ugilq.mongodb.net/myFirstDatabase?retryWrites=true&w=majority',
                     tlsCAFile=certifi.where())
db = client.travel


#################################
##           메인페이지           ##
#################################

# 메인페이지 Route
@app.route('/')
def home():
    # 토큰값 가져오기
    accessToken_receive = request.cookies.get(app.config['ACCESSTOKEN'])
    refreshToken_receive = request.cookies.get(app.config['REFRESHTOKEN'])

    # 토큰들이 유효한지 확인
    isValidAccessToken = getAccessToken()
    isValidRefreshToken = getRefreshToken()

    if isValidAccessToken and isValidRefreshToken:
        # AccessToken과 RefreshToken 모두 유효 => 계속 진행

        # accessToken_receive Decode
        payload = jwt.decode(accessToken_receive, app.config['SECRET_KEY'], algorithms=['HS256'])

        # Decode한 Token값에 저장된 id로 DB의 유저 정보 찾기
        user_info = db.users.find_one({"id": payload["id"]})

        # 찾은 유저를 return
        return render_template('index.html', user=user_info)

    elif isValidAccessToken is not True and isValidRefreshToken:
        # AccessToken 만료 RefreshToken 유효 => AccessToken 재발급

        # refreshToken_receive Decode
        old_payload = jwt.decode(refreshToken_receive, app.config['SECRET_KEY'], algorithms=['HS256'])

        # accessToken 생성과 encode
        payload = {
            'id': old_payload['id'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=app.config['ACCESSTOKENVALIDTIME'])
        }
        accessToken = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

        # Decode한 Token값에 저장된 id로 DB의 유저 정보 찾기
        user_info = db.users.find_one({"id": old_payload["id"]})

        # make_respons에 돌려줄 페이지를 넣는다. accessToken을 return시에 쿠키에 저장
        result = make_response(render_template('index.html', user=user_info))
        result.set_cookie("accessToken", accessToken)
        return result

    elif isValidAccessToken and isValidRefreshToken is not True:
        # AccessToken 유효 RefreshToken 만료 => RefreshToken 재발급
        old_payload = jwt.decode(accessToken_receive, app.config['SECRET_KEY'], algorithms=['HS256'])
        # refreshToken 생성 및 DB저장
        payload = {
            'id': old_payload['id'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=app.config['REFRESHTOKENVALIDTIME'])
        }
        refreshToken = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

        # 유저 DB에 refreshToken값 업데이트
        db.users.update_one({'id': old_payload['id']}, {'$set': {app.config['REFRESHTOKEN']: refreshToken}})

        # Decode한 Token값에 저장된 id로 DB의 유저 정보 찾기
        user_info = db.users.find_one({"id": old_payload["id"]})

        # make_respons에 돌려줄 페이지를 넣는다. accessToken을 return시에 쿠키에 저장
        result = make_response(render_template('index.html', user=user_info))
        result.set_cookie("refreshToken", refreshToken)
        return result

    else:
        # AccessToken과 RefreshToken 모두 만료 => 로그인 X일 때 메인페이지
        return render_template('index.html', user=None)


# 메인페이지 API
@app.route('/api/plans', methods=['GET'])
def get_plans():
    location = request.args.get('location', "")
    query = request.args.get('query', "")
    sort = request.args.get('sort', "date")
    page = request.args.get('page', 1, type=int)
    limit = 12

    sorting = 1 if sort == "과거" else -1

    option = {}

    if len(location) > 0:
        option['location'] = location

    if len(query) > 0:
        option['location'] = query

    plans = list(db.plan.find(option).skip((page - 1) * limit).limit(limit).sort("date", sorting))

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


@app.route('/api/plans/<id>', methods=['GET'])
def get_plan(id):
    plan = db.plan.find_one({'_id': ObjectId(id)})
    plan['_id'] = str(plan['_id'])
    return jsonify(plan)

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


app.register_blueprint(blue_login)


#################################
        ##  PLANS  ##
#################################


@app.route("/plan", methods=["POST"])
@home_decorator()
def plan_post():
    image_receive = request.form['image_give']
    title_receive = request.form['title_give']
    area_receive = request.form['area_give']
    location_receive = request.form['location_give']
    dateStart_receive = request.form['dateStart_give']
    dateEnd_receive = request.form['dateStart_give']
    detailTable_receive = request.form['tableData_give']

    doc = {
        'image':image_receive,
        'title':title_receive,
        'area':area_receive,
        'location':location_receive,
        'dateStart':dateStart_receive,
        'dateEnd':dateEnd_receive,
        'detailTable': detailTable_receive,
    }
    db.plans.insert_one(doc)

    return jsonify({'msg':'저장 완료!'})

# Plns 가져오기
@app.route('/plan', methods=['GET'])
def plan_get():
    # try :
    #     plans = list(db.plans.find({}).sort("date", -1).limit(20))
    #     for plan in plans:
    #         plan["_id"] = str(plan["_id"])

        plan_list = list(db.plans.find({}, {'_id': False}))
        return jsonify({'plans': plan_list})



# 프로필 블루프린트 등록 (연결)
app.register_blueprint(user.bp)


## local port
if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

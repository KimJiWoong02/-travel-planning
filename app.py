from flask import Flask, render_template, jsonify, request, session, redirect, url_for, make_response
from pymongo import MongoClient
import certifi
import math
# jwt 패키지 사용
import jwt

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


app.register_blueprint(blue_login)


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

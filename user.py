import jwt
from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from pymongo import MongoClient

SECRET_KEY = 'SPARTA'

client = MongoClient(
    'mongodb+srv://test:sparta@cluster0.ugilq.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')
db = client.travel

bp = Blueprint('user', __name__, url_prefix='/user')


@bp.route('/<username>')
def user(username):
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        status = (username == payload["id"])

        user_info = db.testuser.find_one({"username": username}, {"_id": False})
        return render_template('user.html', user_info=user_info, status=status)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@bp.route('/edit', methods=['POST'])
def edit_profile():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        name_receive = request.form["username"]

        # 파일 받아서 저장하는 방법
        file = request.files["file_give"]
        save_to = 'static/mypicture.jpg'
        file.save(save_to)

        new_doc = {
            "profile_name": name_receive
        }
        db.testuser.update_one({'username': payload['id']}, {'$set': new_doc})
        return jsonify({"result": "success", 'msg': '프로필을 업데이트했습니다.'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

import os
import jwt
from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from pymongo import MongoClient
from werkzeug.utils import secure_filename
import config
import certifi

from checkToken import home_decorator

client = MongoClient('mongodb+srv://test:sparta@cluster0.ugilq.mongodb.net/myFirstDatabase?retryWrites=true&w=majority',
                     tlsCAFile=certifi.where())
db = client.travel

bp = Blueprint('user', __name__, url_prefix='/user')


@bp.route('/mypage', methods=['GET'])
@home_decorator()
def user():
    token_receive = request.cookies.get(config.ACCESSTOKEN)
    try:
        payload = jwt.decode(token_receive, config.SECRET_KEY, algorithms=['HS256'])

        user_info = db.users.find_one({"id": payload['id']}, {"_id": False})
        return render_template('user.html', user_info=user_info)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@bp.route('/mypage', methods=['POST'])
def user_plan():
    id = request.form['id']

    myplan_list = list(db.plans.find({"id": id}, {"_id": False}))
    return jsonify({'myplan': myplan_list})


@bp.route('/edit', methods=['POST'])
def edit_profile():
    token_receive = request.cookies.get(config.ACCESSTOKEN)
    try:
        payload = jwt.decode(token_receive, config.SECRET_KEY, algorithms=['HS256'])
        id = payload['id']
        name_receive = request.form['name_give']
        new_doc = {
            'name': name_receive
        }
        if 'file_give' in request.files:
            file = request.files['file_give']

            filename = secure_filename(file.filename)
            extension = filename.split('.')[-1]
            file_path = f'profile_pics/{id}.{extension}'

            file.save(os.path.join(bp.root_path, './static/', file_path))

            new_doc['img'] = filename
            new_doc['img_path'] = file_path

        db.users.update_one({'id': payload['id']}, {'$set': new_doc})

        return jsonify({"result": "success", 'msg': '프로필을 업데이트했습니다.'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

import os
import jwt
from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from pymongo import MongoClient
from werkzeug.utils import secure_filename
import config
import certifi

from checkToken import home_decorator, getTokenInID

client = MongoClient('mongodb+srv://test:sparta@cluster0.ugilq.mongodb.net/myFirstDatabase?retryWrites=true&w=majority',
                     tlsCAFile=certifi.where())
db = client.travel

bp = Blueprint('user', __name__, url_prefix='/user')


@bp.route('/mypage', methods=['GET'])
@home_decorator()
def user():
    try:
        # Access, Refresh 토큰을 검사하여 유효한 토큰이 있을 시 사용자의 ID를 반환, 없을 시 None
        user_id = getTokenInID()
        if user_id is not None:
            user_info = db.users.find_one({"user_id": user_id}, {"_id": False})
            myplan_list = list(db.plans.find({"user_id": user_id}, {"_id": False}))
            return render_template('user.html', user_info=user_info, myplan_list=myplan_list)
        else:
            return redirect(url_for("home"))

    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@bp.route('/edit', methods=['POST'])
@home_decorator()
def edit_profile():
    try:
        # Access, Refresh 토큰을 검사하여 유효한 토큰이 있을 시 사용자의 ID를 반환, 없을 시 None
        user_id = getTokenInID()

        if user_id is not None:
            name_receive = request.form['name_give']
            new_doc = {
                'user_name': name_receive
            }
            if 'file_give' in request.files:
                file = request.files['file_give']

                filename = secure_filename(file.filename)
                extension = filename.split('.')[-1]
                file_path = f'profile_pics/{user_id}.{extension}'

                file.save(os.path.join(bp.root_path, './static/', file_path))

                new_doc['img'] = filename
                new_doc['img_path'] = file_path

            db.users.update_one({'user_id': user_id}, {'$set': new_doc})

            return jsonify({"result": "success", 'msg': '프로필을 업데이트했습니다.'})
        else:
            raise Exception

    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

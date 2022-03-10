from flask import Flask, render_template, jsonify, request, session, redirect, url_for, Blueprint, make_response, current_app
from pymongo import MongoClient
import certifi
# jwt 패키지 사용
import jwt
# 토큰에 만료시간을 줘야하기 때문에, datetime 모듈도 사용
import datetime
# decorator jwt 검사를 위한 미들웨어로 활용
from functools import wraps

client = MongoClient('mongodb+srv://test:sparta@cluster0.ugilq.mongodb.net/myFirstDatabase?retryWrites=true&w=majority',
                     tlsCAFile=certifi.where())
db = client.travel


#################################
##        토큰 검사 미들웨어      ##
#################################
def home_decorator():
    def _home_decorator(f):
        @wraps(f)
        def __home_decorator(*args, **kwargs):
            accessToken_receive = request.cookies.get(current_app.config['ACCESSTOKEN'])
            refreshToken_receive = request.cookies.get(current_app.config['REFRESHTOKEN'])

            # AccessToken이 유효한가? True or False
            isValidAccessToken = getAccessToken()

            # RefreshToken이 유효한가? True or False
            isValidRefreshToken = getRefreshToken()

            if isValidAccessToken and isValidRefreshToken:
                # AccessToken과 RefreshToken 모두 유효 => 계속 진행
                result = f()
                return result

            elif isValidAccessToken is not True and isValidRefreshToken:
                # AccessToken 만료 RefreshToken 유효 => AccessToken 재발급
                old_payload = jwt.decode(refreshToken_receive, current_app.config['SECRET_KEY'], algorithms=['HS256'])
                payload = {
                    'id': old_payload['id'],
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=current_app.config['ACCESSTOKENVALIDTIME'])
                }
                accessToken = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')

                result = make_response(f())
                result.set_cookie("accessToken", accessToken)
                return result

            elif isValidAccessToken and isValidRefreshToken is not True:
                # AccessToken 유효 RefreshToken 만료 => RefreshToken 재발급
                old_payload = jwt.decode(accessToken_receive, current_app.config['SECRET_KEY'], algorithms=['HS256'])
                # refreshToken 생성 및 DB저장
                payload = {
                    'id': old_payload['id'],
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=current_app.config['REFRESHTOKENVALIDTIME'])
                }
                refreshToken = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')

                db.users.update_one({'user_id': old_payload['id']}, {'$set': {current_app.config['REFRESHTOKEN']: refreshToken}})

                result = make_response(f())
                result.set_cookie("refreshToken", refreshToken)
                return result

            else:
                # AccessToken과 RefreshToken 모두 만료 => 로그인 페이지
                return redirect(url_for("login"))

        return __home_decorator

    return _home_decorator


def getAccessToken():
    accessToken_receive = request.cookies.get(current_app.config['ACCESSTOKEN'])
    try:
        jwt.decode(accessToken_receive, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        return True
    except jwt.ExpiredSignatureError:  # 유효기간 만료된 토큰 디코드 시
        return False
    except jwt.exceptions.DecodeError:  # 해당 token이 올바르게 디코딩되지 않았다면
        return False


def getRefreshToken():
    refreshToken_receive = request.cookies.get(current_app.config['REFRESHTOKEN'])
    try:
        payload = jwt.decode(refreshToken_receive, current_app.config['SECRET_KEY'], algorithms=['HS256'])

        # 유저 ID로 유저 DB SELECT
        user_info = db.users.find_one({"user_id": payload['id']})

        # 쿠키에 저장된 refreshToken와 DB에 저장된 refreshToken가 같은지 비교
        if refreshToken_receive == user_info[current_app.config['REFRESHTOKEN']]:
            return True
        else:
            return False
    except jwt.ExpiredSignatureError:  # 유효기간 만료된 토큰 디코드 시
        return False
    except jwt.exceptions.DecodeError:  # 해당 token이 올바르게 디코딩되지 않았다면
        return False
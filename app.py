from flask import Flask, render_template, jsonify, request
app = Flask(__name__)

import requests
from bs4 import BeautifulSoup


# from pymongo import MongoClient
from pymongo import MongoClient
import certifi
ca = certifi.where()
client = MongoClient('mongodb+srv://test:sparta@cluster0.ugilq.mongodb.net/myFirstDatabase?retryWrites=true&w=majority',tlsCAFile=ca)
db = client.travel


# jinja test





## HTML을 주는 부분
@app.route('/')
def plans():
    myname = "Sparta"
    return render_template('card.html', name=myname)



## API 역할을 하는 부분



@app.route("/plan", methods=["POST"])
def plan_post():
    title_receive = request.form['title_give']
    area_receive = request.form['area_give']
    location_receive = request.form['location_give']
    dateStart_receive = request.form['dateStart_give']
    dateEnd_receive = request.form['dateStart_give']
    share_receive = request.form['share_give']

    doc = {
        'title':title_receive,
        'area':area_receive,
        'location':location_receive,
        'dateStart':dateStart_receive,
        'dateEnd':dateEnd_receive,
        'share':share_receive,
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

#

if __name__ == '__main__':
   app.run('0.0.0.0',port=5000,debug=True)
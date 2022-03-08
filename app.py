import datetime
from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
import math

app = Flask(__name__)

client = MongoClient('mongodb+srv://test:sparta@cluster0.xedql.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.plan


@app.route('/')
def home():
    return render_template('index.html')

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

    plans = list(db.plan.find(option).skip((page-1)*limit).limit(limit).sort(sort, -1))

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


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
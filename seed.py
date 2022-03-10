import certifi
from pymongo import MongoClient, InsertOne
import datetime

ca = certifi.where()
client = MongoClient('mongodb+srv://test:sparta@cluster0.ugilq.mongodb.net/myFirstDatabase?retryWrites=true&w=majority', tlsCAFile=certifi.where())
db = client.travel

def get_dummy():
    return {
        "image": "https://acs-h.assetsadobe.com/is/image//content/dam/cen/96/44/09644-scicon7-llamacxd.jpg/?$responsive$&wid=300&qlt=90",
        "title": "가족과 가는 강화도 여행",
        "date_start": "2022-03-09",
        "date_end": "2022-03-12",
        "date": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "area": "경기도",
        "host": "AA",
        "share": ["BB", "CC"],
        "location": ["경기도", "수원", "송죽동"],
        "day_plan": [{
            "day": "1일차",
            "location": "수원",
            "address": "1번가",
            "description": "놀러간다"
        },{
            "detail_day": "2일차",
            "location": "서울",
            "address": "2번가",
            "description": "영화본다"
        }],
        "like": 100
    }


db.plan.bulk_write([InsertOne(get_dummy()) for i in range(100)])

print("it works")

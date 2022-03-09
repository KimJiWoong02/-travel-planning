import certifi
from pymongo import MongoClient, InsertOne

ca = certifi.where()
client = MongoClient('mongodb+srv://test:sparta@cluster0.ugilq.mongodb.net/myFirstDatabase?retryWrites=true&w=majority', tlsCAFile=certifi.where())
db = client.travel

def get_dummy():
    return {
        "imageUrl": "https://acs-h.assetsadobe.com/is/image//content/dam/cen/96/44/09644-scicon7-llamacxd.jpg/?$responsive$&wid=300&qlt=90",
        "title": "가족과 가는 강화도 여행",
        "hashTags": ["1박 2일", "가족여행", "4인이상추천"],
        "location": ["경기도", "수원", "송죽동"]
    }


db.plan.bulk_write([InsertOne(get_dummy()) for i in range(100)])

print("it works")

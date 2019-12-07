import pymongo
import datetime
from bson.objectid import ObjectId
import requests
import json

headers = {'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoic2RnZGZzZ2ZkZyIsImVtYWlsIjoiaG9hbmd0cm9uZ21pbmhkdWNzdGFyQGdtYWlsLmNvbSIsImpvaW5fZGF0ZSI6IjIwMTktMTAtMDlUMTc6NTg6NTIuOTY5WiIsImlkIjoiNWQ5ZTFmZGM2YzE2YTIzNWQ0Y2JiZTFiIiwiaWF0IjoxNTc0MTM5NjYxLCJleHAiOjE1NzkzMjM2NjF9.clRPgYzLi9uBf3U5XknJ2zkbrbo09QYVPTIZ1UTSZpI'}


class Database:
    def __init__(self):
        self.headers = headers

    def updateResume(self, id, data):
        data["status"] = "Processed"
        rq = requests.put(
            'http://dev.shieldmanga.icu:3000/api/resumes/' + id, headers=headers, json=data)

    def updateRanked(self, id, data):
        data["status"] = "Processed"
        rq = requests.put(
            'http://dev.shieldmanga.icu:3000/api/positions/' + id + '/ranked', headers=headers, json=data)

    def getResume(self, id):
        return self.collection.find({}, {"_id": ObjectId(id)})

    def getRegularRate(self):
        return requests.get('http://dev.shieldmanga.icu:3000/api/positions/getrate', headers=headers)


# db = Database();
# allRate = db.getRegularRate().json()
# for r in allRate:
#     print(r)

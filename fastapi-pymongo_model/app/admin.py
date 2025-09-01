import os
from pymongo import MongoClient
from bson import ObjectId

os.environ["MONGO_URI"] = "mongodb://localhost:27017/"


class Model:
    def __init__(self):
        self.mongo_client = MongoClient(os.environ["MONGO_URI"])
        self.db = self.mongo_client.crudpymongo
        self.intent = self.db['intent']

    def add_model_active(self, name):
        self.model_active.insert_one({
            "model_name": name
        })

    def add_intent(self, intent, description):
        self.intent.insert_one({
            "intent_name": intent,
            "description": description
        })

    def set_intent(self, id, intent, description):
        self.intent.update_one(
            {"_id": ObjectId(id)},
            {"$set":
                {
                    "intent_name": intent,
                    "description": description,
                }
            }
        )

    def get_intent(self):
        return list(self.intent.find())

    def close_conn(self):
        self.mongo_client.close()
        print("obj destroy")

    def remove_intent(self, id):
        self.intent.delete_one({'_id': ObjectId(id)})

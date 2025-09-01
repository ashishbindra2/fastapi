from pymongo import MongoClient
import os
import logging

os.environ["MONGO_URI"] = "mongodb://localhost:27017/"


class User:
    def __init__(self):
        """
        :param client_id: takes client id as parameter to store intent flow per client wise
        """

        self.mongo_client = MongoClient(os.environ["MONGO_URI"])
        self.db = self.mongo_client.chatflowdb
        self.user_table = self.db['User']
        self.logger = logging.getLogger(__name__)


    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self):
        self.mongo_client.close()
        print("MongoDB connection closed.")

    def add_user(self, user_data):
        """
        :param user_data:
        :return: None
        """
        existing_user = self.user_table.find_one({"username": user_data["username"]})
        if existing_user:
            return {"error": f"User with username {user_data['username']} already exists."}
        else:
            self.user_table.insert_one(user_data)
            return {"message": f"User {user_data['username']} added successfully."}

    # @staticmethod

    def get_user_name(self, name):
        """
        :param name: The username to search for in the database.
        :return: The response from the database query, or None if the user is not found.
        """
        try:
            response = self.user_table.find_one({"username": name})
            if response:
                self.logger.debug("User found: %s", response)
                return response
            else:
                self.logger.info("User not found for username: %s", name)
                return None
        except Exception as e:
            self.logger.error("Error while querying the database: %s", str(e))
            # Handle the exception or re-raise based on your requirements
            return str(e)

    def get_users(self):
        """
        :return: calls resolve api internally, returns a list of user documents from the database
        """
        cursor = self.user_table.find()
        users = list(cursor)  # Convert the cursor to a list of documents

        if users:
            return users
        return None


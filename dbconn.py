from datetime import datetime
from pymongo import MongoClient


class Dbconn:
    def __init__(self):
        self.dbuser = "inictelbotadmin"
        self.dbpass = "QOPakasha123"
        self.dbnode = 'cluster0-5ejgb.azure.mongodb.net/test?retryWrites=true&w=majority'
        self.db = None
        self.connection = None
        self.connect()
        # mongodb+srv://inictelbotadmin:<password>@cluster0-5ejgb.azure.mongodb.net/test?retryWrites=true&w=majority

    def connect(self):
        try:
            self.connection = MongoClient('mongodb+srv://' + self.dbuser + ':' + self.dbpass + '@' + self.dbnode)
        except TimeoutError:
            exit("Error: Unable to connect to the database")
        self.db = self.connection['inictelbotdb']

    def get_collection(self, collection_name):
        if self.db is None:
            self.connect()
        return self.db[collection_name]

    def add_enrollment(self, new_enrollment):
        if self.db is None:
            self.connect()
        collection = self.db['enrollments']
        enrollment_id = collection.insert_one(new_enrollment[1]).inserted_id
        # enrollment_id = collection.insert_one(new_enrollment[1], session=self.connection.start_session(causal_consistency=True, default_transaction_options=None)).inserted_id
        return True if enrollment_id is not None else False

    def get_enrollment(self, user_id):
        if self.db is None:
            self.connect()
        collection = self.db['enrollments']
        record = collection.find_one({"user": user_id})
        return True if record is not None else False

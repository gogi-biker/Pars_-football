from types import MappingProxyType
from pymongo import MongoClient


class MongoDefault:
    """
    Examples:

    insertUpdate = value from unique key and dict from models class

    select = {"name": "Jamie Vardy"}

    delete = {"name": "Jamie Vardy"}
    """

    def __init__(self, collection, db="football"):
        """
        :param db: DB name
        :param collection: Collection name [players, teams, gameIndicators]
        """
        self.db = db
        self.collection = collection

    def __enter__(self):
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client[self.db]
        self.collection = self.db[self.collection]
        return self

    def insertUpdate(self, value_uniq_key: str, value_to: dict, one: int = 1) -> tuple:
        """
        :param value_uniq_key: Value from uniq key
        :param value_to: Value for update or insert
        :param one: Update one document
        :return: status code
        """
        uniq_key = MappingProxyType({
            self.collection.name == "players": "player",
            self.collection.name == "teams": "name",
            self.collection.name == "gameIndicators": "match"
        })[True]
        old_data = {uniq_key: value_uniq_key}
        new_data = {"$set": value_to}
        if one:
            result = self.collection.update_one(old_data, new_data, upsert=True)
            return result.acknowledged, result.modified_count
        else:
            raise NotImplementedError("Not Implemented case")
            # result = self.collection.update_many()

    def select(self, data: dict) -> dict:
        """
        :param data: Data for search in DB
        :return: Cursor object or empty dict if data not found
        """

        result = self.collection.find(data)
        check = next(result, {})
        if not check:
            return check
        else:
            return self.collection.find(data)

    def delete(self, data: dict, one: int = 1) -> tuple:
        """
        :param data: Data for delete in DB
        :param one: Delete one document
        :return: status code
        """
        if one:
            result = self.collection.delete_one(data)
            return result.acknowledged, result.deleted_count
        else:
            raise NotImplementedError("Not Implemented case")
            # result = self.collection.delete_many(data)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()

    def __str__(self):
        return "Client: {!s}, Collection: {!s}".format(self.client.address, self.collection.name)

    def __repr__(self):
        return "{}({!r}, {})".format(self.__class__.__name__, self.client.address, self.collection.name)

import base64
import io
import csv

from django.conf import settings as app_settings

from pymongo import MongoClient


def connect_to_mongo():
    """
    Establish Mongo Connection
    :return db_client: mongo connection
    """
    mongo_client = MongoClient(app_settings.MONGO_URI)
    db_client = mongo_client[app_settings.MONGO_DB_NAME]

    return db_client


def process_data(data, source):
    if source is not None and source.lower() == 'csv':
        data = process_csv_data(data)
    else:
        data = None

    return data


def process_csv_data(data):
    if data and data['value']:
        content = base64.b64decode(data['value'])
        io_string = io.StringIO(content.decode("utf-8"))
        try:
            reader = csv.DictReader(io_string)
            dict_data = [row for row in reader]
        except Exception as e:
            raise Exception(e)

        return dict_data

    else:
        raise KeyError('Could not find file information.')

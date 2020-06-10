import base64
import io
import csv
import requests
from typing import List

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


def clean_data_columns(data) -> List[dict]:
    """
    Clean data colums to conform to Mongo standards
    :param data: with  malformed keys
    :return data: with cleaned keys
    """
    try:
        dict_keys = list(data[0].keys())

        #  get labels to be updated
        invalid_cols = [col for col in dict_keys if '.' in col or '$' in col]

        #  update data columns
        if invalid_cols:
            for row in data:
                for key in list(row.keys()):
                    if '.' in key or '$' in key:
                        new_key = key.replace('.', '_').replace('$', '_')
                        row[new_key] = row[key]
                        del row[key]
        #  return data with updated keys
        return data
    except (IndexError, TypeError,):
        return data


def process_data(data, source):
    """
    construct Mongo data
    :param data: form or data details
    :param source: data source
    :return data: valid json data to be dumped to mongo
    """
    if source is not None:
        if source.lower() == 'csv':
            return process_csv_data(data)
        if source.lower() == 'kobo' or source.lower() == 'ona':
            return get_form_data(data, source)

    return None


def process_csv_data(data):
    """
    Process csv data to dict list
    :param data: base64 file data
    :return dict_data: dict list
    """
    if data and data['value']:
        content = base64.b64decode(data['value'])
        io_string = io.StringIO(content.decode('utf-8', 'replace'))
        try:
            reader = csv.DictReader(io_string)
            dict_data = [row for row in reader]
        except Exception as e:
            raise Exception(e)

        return clean_data_columns(dict_data)

    else:
        raise KeyError('Could not find file data.')


def generate_geojson_data(table):
    """
    generate Geojson data from table data
    :param table:
    :return: Geojson dict data
    """
    try:
        collection_name = table.name.replace(' ', '_')
    except AttributeError:
        collection_name = table.get('name').replace(' ', '_')

    mongo_client = connect_to_mongo()
    connection = mongo_client[collection_name]
    data = connection.find_one({'table_uuid': str(table.table_uuid)}).get('data')
    longitude_field = table.metadata.get('longitude_field', None)
    latitude_field = table.metadata.get('latitude_field', None)
    geo_location_field = table.metadata.get('geo_point_field', None)
    map_tool_tip_field = table.metadata.get('tool_tip_field', None)
    get_features = []
    if (
            longitude_field is not None and latitude_field is not None
    ) or geo_location_field is not None:

        for row in data:
            feature = get_feature(
                row,
                longitude_field,
                latitude_field,
                geo_location_field,
                map_tool_tip_field
            )
            if feature is not None:
                get_features.append(feature)

        return dict(
            type='FeatureCollection',
            features=get_features
        )


def get_feature(row, longitude_field=None, latitude_field=None, geo_field=None, map_tool_tip_field=None):
    """
      gets fields necessary for displaying the map
      :param row: table data row from mongo
      :param longitude_field: longitude field
      :param latitude_field: latitude field
      :@param geo_field: geoLocation field
      :param map_tool_tip_field: field show on point tooltip
      :return map_feature: Geojson feature object
      """
    if geo_field is not None and geo_field != '':
        lat = row.get(geo_field)[0]
        long = row.get(geo_field)[1]
        if lat is not None and long is not None:
            geometry = dict(
                coordinates=[float(row.get(geo_field)[1]), float(row.get(geo_field)[0])],
                type='Point'
            )
        else:
            geometry = None
    else:
        lat = row.get(latitude_field, None)
        long = row.get(longitude_field, None)
        if lat is not None and long is not None:
            geometry = dict(
                coordinates=[float(row.get(longitude_field)), float(row.get(latitude_field))],
                type='Point'
            )
        else:
            geometry = None

    properties = dict(
        title=row.get(map_tool_tip_field, ''),
        icon='rocket'
    )

    if geometry is None:
        return None

    map_feature = dict(
        type='Feature',
        geometry=geometry,
        properties=properties
    )

    return map_feature


def get_data_source_forms(source):
    """
    Get data source forms
    :param source: data source
    :return forms: array of user accessible forms
    """
    if source.lower() == 'kobo':
        forms = requests.get(
            f'{app_settings.KOBO_URI}/data?format=json',
            headers=dict(Authorization=f'Token {app_settings.KOBO_API_KEY}')
        )
        return forms.json()
    if source.lower() == 'ona':
        projects = requests.get(
            f'{app_settings.ONA_URI}/projects',
            headers=dict(Authorization=f'Token {app_settings.ONA_API_KEY}')
        )
        forms = list()
        for project in projects.json():
            forms += [form for form in project.get('forms')]

        return forms

    if source.lower() == 'surveycto':
        # TODO:- Implement survey-cto data import
        url = app_settings.SURVEY_CTO_URI
        return None

    return None


def get_form_data(form_details, source):
    """
    get form data from the source using form ID
    :param form_details: form details dict
    :param source: data source
    :return data: form data
    """
    if source.lower() == 'kobo':
        data = requests.get(
            form_details.get('url'),
            headers=dict(Authorization=f'Token {app_settings.KOBO_API_KEY}')
        )
        return data.json()

    return None

from maps.models import MapLayer
from tables.utils import (connect_to_mongo, )


def generate_geojson_point_data(layer: MapLayer) -> bool:
    """
    generate Geojson data from table data
    :layer: map layer
    :return: Geojson dict data
    """
    try:
        collection_name = layer.table.name.replace(' ', '_')
    except AttributeError:
        collection_name = layer.get('table').get('name').replace(' ', '_')

    # connect to mongo and get data
    mongo_client = connect_to_mongo()
    connection = mongo_client[collection_name]
    data = connection.find_one({'table_uuid': str(layer.table.table_uuid)}).get('data')

    longitude_field = layer.longitude_field
    latitude_field = layer.latitude_field
    geo_location_field = layer.geo_point_field
    map_tool_tip_fields = layer.tool_tip_fields
    get_features = []

    if (longitude_field and latitude_field) or geo_location_field:

        for row in data:
            feature = get_feature(
                row,
                longitude_field,
                latitude_field,
                geo_location_field,
                map_tool_tip_fields
            )
            if feature is not None:
                get_features.append(feature)

        map_feat_collection = dict(
            type='FeatureCollection',
            features=get_features
        )

        # save collection data to Mongo
        try:
            layer_connection = mongo_client[layer.name.replace(' ', '').replace('.', '').replace('$', '')]
            layer_data = dict(layer_uuid=str(layer.layer_uuid), geodata=map_feat_collection)
            layer_connection.insert_one(layer_data)
        except Exception as e:
            raise Exception(e)

        return True


def get_feature(row, longitude_field=None, latitude_field=None, geo_field=None, map_tool_tip_fields=None) -> dict:
    """
      gets fields necessary for displaying the map
      :param row: table data row from mongo
      :param longitude_field: longitude field
      :param latitude_field: latitude field
      :@param geo_field: geoLocation field
      :param map_tool_tip_fields: field show on point tooltip
      :return map_feature: Geojson feature object
      """
    if geo_field is not None and geo_field != '':
        try:
            # configure geometry property
            lat = row.get(geo_field)[0]
            long = row.get(geo_field)[1]
            geometry = dict(
                coordinates=[float(long), float(lat)],
                type='Point'
            )
        except IndexError:
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

    # set up tool tip property
    properties = dict(icon='rocket')
    for field in map_tool_tip_fields:
        properties.update({field: row.get(field, None)})
    properties = {}

    # return None if there is no geometry value for the feature
    if geometry is None:
        return None

    map_feature = dict(
        type='Feature',
        geometry=geometry,
        properties=properties
    )

    return map_feature


def get_layer_collection_name(layer: MapLayer) -> str:
    """
    construct layer geodata collection name
    :param layer:
    :return:
    """
    return f'{layer.name}_{layer.id}'.replace(' ', '').replace('.', '').replace('$', '')

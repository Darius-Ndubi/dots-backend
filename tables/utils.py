import base64
import io
import csv


def process_data(data, source):
    if source is not None and source.toLower() == 'csv':
        data = process_csv_data(data)
    else:
        data = None

    return data


def process_csv_data(data):
    if data['file'] and data['file']['value']:
        content = base64.b64decode(data['file']['value'])
        io_string = io.StringIO(content.decode("utf-8"))
        try:
            reader = csv.DictReader(io_string, delimeter=',')
            dict_data = [row for row in reader]
        except Exception as e:
            raise Exception(e)

        return dict_data

    else:
        raise KeyError('Could not find file information.')

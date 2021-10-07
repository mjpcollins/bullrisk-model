import pandas as pd
from google.cloud.storage import Client
from config.conf import settings


def read_from_storage(event):
    bucket = Client(settings['project']).bucket(event['bucket'])
    blob = bucket.blob(event['name'])
    file = blob.download_as_string()
    data = pd.ExcelFile(file)
    df = data.parse(0, skiprows=0)
    df['source'] = event['name']
    return df


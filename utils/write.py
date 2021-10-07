from google.cloud.storage import Client
from config.conf import settings
import requests


def write_output(df, event):
    fix_columns(df)
    write_to_gcs(df, event=event)
    write_to_bq(event)


def fix_columns(df):
    columns = list(df.columns)
    new_cols = [fix_column(c) for c in columns]
    df.columns = new_cols


def fix_column(col):
    col = col.replace(' ', '_')
    col = col.replace('(', '_')
    col = col.replace(')', '')
    col = col.replace('__', '_')
    return col


def write_to_gcs(df, event):
    bucket = Client(settings['project']).bucket(settings['egress-bucket'])
    name = format_file_name(event['name'])
    blob = bucket.blob(name)
    csv = df.to_csv(index=False)
    blob.upload_from_string(csv)
    event['uri'] = get_blob_uri(blob)




def get_blob_uri(blob):
    name = blob.name
    bucket = blob.bucket.name
    uri = f"gs://{bucket}/{name}"
    return uri


def format_file_name(name, no_csv=False):
    name = name.split('.')
    if no_csv:
        return ".".join(name[:-1])
    return ".".join(name[:-1] + ["csv"])


def write_to_bq(event):
    url = settings['bigquery-writer']
    data = {'project': settings['project'],
            'dataset': settings['dataset'],
            'name': 'model_output',
            'uri': event['uri'],
            'bucket': settings['egress-bucket']}
    r = requests.post(url=url,
                      json=data)
    print(r.text)

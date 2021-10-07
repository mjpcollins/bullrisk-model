from flask import Flask, request, jsonify
from config.conf import settings
from utils.read import read_from_storage
from utils.write import write_output
app = Flask(__name__)


@app.route('/')
def home():
    return 'OK'


@app.route('/model', methods=['POST'])
def model():
    event = request.json
    print(f'Input: {event}')
    df = read_from_storage(event)
    print(f'df head: {df.head()}')
    write_output(df, event)
    return jsonify({'result': 'OK'})


def run():
    app.run(host='0.0.0.0',
            port=settings['port'])


def debug():
    app.run(host='0.0.0.0',
            port='5000')


if __name__ == '__main__':
    run()

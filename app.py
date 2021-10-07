from flask import Flask
from config.conf import settings
app = Flask(__name__)


@app.route('/')
def home():
    return 'OK'


def run():
    app.run(host='0.0.0.0',
            port=settings['port'])


def debug():
    app.run(host='0.0.0.0',
            port='5000')


if __name__ == '__main__':
    run()

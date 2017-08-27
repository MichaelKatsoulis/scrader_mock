from __future__ import print_function
import flask
import json
from flask.ext.cors import CORS
import os
import signal
import config
from scrader_handler import scrader_poll
from scrader_handler import fetch_news_from_db
import mongo

DEBUG = False  # Enable this to print python crashes and exceptions

app = flask.Flask(__name__)

# Make cross-origin AJAX possible (for all domains on all routes)
CORS(app, resources={r"*": {"origins": "*"}})


@app.route('/scrader'.format(methods=['GET']))
def get_html():
    """ GET Server Status API endpoint
        Args:
        Returns:
            dict: A JSON object containing the nfvacc server status information
    """

    return flask.render_template('index.html')


@app.route('/status'.format(methods=['GET']))
def get_server_status():
    """ GET Server Status API endpoint
        Args:
        Returns:
            dict: A JSON object containing the nfvacc server status information
    """

    response_data = {'server_status': 'OK'}
    status = 200 if response_data is not None else 403
    js = json.dumps(response_data, indent=2)
    return flask.Response(js,
                          status=status,
                          mimetype='application/json')


@app.route('/latest_news'.format(methods=['GET']))
def get_latest_news():
    """ GET Server Status API endpoint
        Args:
        Returns:
            dict: A JSON object containing the nfvacc server status information
    """
    response_data = fetch_news_from_db()
    status = 200 if response_data is not None else 403
    js = json.dumps(response_data, indent=2)
    return flask.Response(js,
                          status=status,
                          mimetype='application/json')


def signal_sigint_handler(rec_signal, rec_frame):
    os._exit(1)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_sigint_handler)

    # set the flask logger => ERROR: do not print API calls
    import logging

    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

    res = mongo.init_database()
    if res is None:
         os._exit(1)

    print (res)
    scrader_poll(companies=config.companies, sources=config.sources)
    app.run(host=config.HOST, port=config.PORT, debug=DEBUG)

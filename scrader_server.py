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


@app.route('/news/<company>'.format(methods=['GET']))
def get_news(company):
    """ GET Server Status API endpoint
        Args:
        Returns:
            dict: A JSON object containing the nfvacc server status information
    """

    print("Company is ")
    print(company)

    response_data = {
        "messages": [{
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "generic",
                    "elements": [{
                        "title": "What Amazon knows: 'The war for retail will be won in groceries'",
                        "image_url": "http://i2.cdn.turner.com/money/dam/assets/170825082748-whole-foods-fresh-fruit-apples-1024x576.jpg",
                        "subtitle": "Amazon believes the future of grocery shopping is online.",
                        "item_url": "http://money.cnn.com/2017/08/25/technology/business/amazon-whole-foods-strategy/index.html",
                        "buttons": [{
                            "type": "web_url",
                            "url": "http://money.cnn.com/2017/08/25/technology/business/amazon-whole-foods-strategy/index.html",
                            "title": "CNN.COM"
                        }]
                    }, {
                        "title": "Ocado Taps Amazon's Alexa for Voice Ordering in Convenience Push",
                        "image_url": "https://assets.bwbx.io/images/users/iqjWHBFdfxIU/i4GOoR9HbhHg/v0/1000x-1.jpg",
                        "subtitle": "U.K. online grocer Ocado Group Plc is teaming up with Amazon.com Inc.",
                        "item_url": "https://petersapparel.parseapp.com/view_item?item_id=101",
                        "buttons": [{
                            "type": "web_url",
                            "url": "https://petersapparel.parseapp.com/view_item?item_id=101",
                            "title": "BLOOMBERG.COM"
                        }]
                    }]
                }
            }
        }]
    }

    status = 200 if response_data is not None else 403
    js = json.dumps(response_data, indent=2)
    return flask.Response(js,
                          status=status,
                          mimetype='application/json')


@app.route('/top_stocks_new'.format(methods=['GET']))
def get_top_stocks_new():
    """ GET Server Status API endpoint
        Args:
        Returns:
            dict: A JSON object containing the nfvacc server status information
    """
    response_data = {
        "messages": [
            {
              "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "button",
                    "text": "Great choice! These are today's top positive stocks",
                    "buttons": [
                        {
                              "type": "show_block",
                              "block_name": "Positive",
                              "title": "Amazon"
                        },
                        {
                              "type": "show_block",
                              "block_name": "Positive",
                              "title": "Apple"
                        },
                        {
                              "type": "show_block",
                              "block_name": "Positive",
                              "title": "Adidas"
                        }
                    ]
                }
              }
            }
        ]
    }
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

    # print (res)
    # scrader_poll(companies=config.companies, sources=config.sources)
    app.run(host=config.HOST, port=config.PORT, debug=DEBUG)

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

    # response_data = {
    #     "messages": [
    #         {
    #             "attachment": {
    #                 "type": "template",
    #                 "payload": {
    #                     "template_type": "list",
    #                     "top_element_style": "compact",
    #                     "elements": [
    #                         {
    #                             "title": "cnn.com",
    #                             "image_url":
    #                                 "http://i2.cdn.turner.com/money/dam/assets/170825082748-whole-foods-fresh-fruit-apples-1024x576.jpg",
    #
    #                             "buttons": [
    #                                 {
    #                                   "type": "web_url",
    #                                   "url": "http://money.cnn.com/2017/08/25/technology/business/amazon-whole-foods-strategy/index.html",
    #                                   "title": "What Amazon knows"
    #                                 }
    #                             ]
    #                         },
    #                         {
    #                             "title": "bloomberg.com",
    #                             "image_url": "https://assets.bwbx.io/images/users/iqjWHBFdfxIU/i4GOoR9HbhHg/v0/1000x-1.jpg",
    #                             "buttons": [
    #                                 {
    #                                     "type": "web_url",
    #                                     "url": "https://www.bloomberg.com/news/articles/2017-08-29/ocado-taps-amazon-s-alexa-for-voice-ordering-in-convenience-push",
    #                                     "title": "Ocado Taps Amazon's Alexa"
    #                                 }
    #                             ]
    #                         }
    #                     ]
    #                 }
    #             }
    #         }
    #     ]
    # }

    response_data = {
         "messages": [
            {
              "attachment":{
                "type":"template",
                "payload":{
                  "template_type":"generic",
                  "elements":[
                    {
                      "title":"Classic White T-Shirt",
                      "image_url": "http://i2.cdn.turner.com/money/dam/assets/170825082748-whole-foods-fresh-fruit-apples-1024x576.jpg",
                      "subtitle":"Soft white cotton t-shirt is back in style",
                      "buttons":[
                        {
                          "type":"web_url",
                          "url":"https://petersapparel.parseapp.com/view_item?item_id=100",
                          "title":"View Item"
                        }
                      ]
                    },
                    {
                      "title":"Classic Grey T-Shirt",
                      "image_url": "https://assets.bwbx.io/images/users/iqjWHBFdfxIU/i4GOoR9HbhHg/v0/1000x-1.jpg",
                      "subtitle":"Soft gray cotton t-shirt is back in style",
                      "buttons":[
                        {
                          "type":"web_url",
                          "url":"https://petersapparel.parseapp.com/view_item?item_id=101",
                          "title":"View Item"
                        }
                      ]
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


@app.route('/top_stocks'.format(methods=['GET']))
def get_top_stocks():
    """ GET Server Status API endpoint
        Args:
        Returns:
            dict: A JSON object containing the nfvacc server status information
    """

    response_data = {
 "messages": [
    {
      "attachment":{
        "type":"template",
        "payload":{
          "template_type": "list",
          "top_element_style": "compact",
          "elements":[
            {
              "title":"Amazon",
              "image_url":"https://www.wired.com/wp-content/uploads/2016/04/amazon-a-logo-1200x630.jpg",
            
              "buttons":[
                {
                    "type": "show_block",
                    "block_name": "Amazon_news",
                    "title": "Check out the news!"
                }
              ]
            },
            {
              "title":"Apple",
              "image_url": "https://www.apple.com/ac/structured-data/images/knowledge_graph_logo.png?201703170823",
              "buttons": [
                {
                  "type": "show_block",
                  "block_name": "Apple_news",
                  "title": "Check out the news!"
                }
              ]
            },
         {
              "title":"Adidas",
              "image_url": "https://mymall.vn/static/images/2014/12/02/1417490727_adidas.jpg",
              "buttons": [
                {
                  "type": "show_block",
                  "block_name": "Addidas_news",
                  "title": "Check out the news!"
                }
              ]
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
                              "block_name": "Amazon_news",
                              "title": "Amazon"
                        },
                        {
                              "type": "show_block",
                              "block_name": "Apple_news",
                              "title": "Apple"
                        },
                        {
                              "type": "show_block",
                              "block_name": "Addidas_news",
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

    print (res)
    scrader_poll(companies=config.companies, sources=config.sources)
    app.run(host=config.HOST, port=config.PORT, debug=DEBUG)

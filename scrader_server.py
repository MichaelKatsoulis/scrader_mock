from __future__ import print_function
import flask
import json
from flask.ext.cors import CORS
from flask import request
import os
import signal
import copy
import config
from scrader_handler import scrader_poll
from scrader_handler import fetch_news_from_db
import mongo

DEBUG = False  # Enable this to print python crashes and exceptions

app = flask.Flask(__name__)

# Make cross-origin AJAX possible (for all domains on all routes)
CORS(app, resources={r"*": {"origins": "*"}})

USERS = []


@app.route('/scrader/companies/<user_id>'.format(methods=['GET']))
def get_html(user_id):
    """ GET Server Status API endpoint
        Args:
        Returns:
            dict: A JSON object containing the nfvacc server status information
    """
    name = "None"
    for user in USERS:
        if user.get('user_id') == user_id:
            name = user.get('name')

    #print('heeee')
    #print(user_id)
    #print(name)
    return flask.render_template('index1.html', name=name, user_id=user_id)


@app.route('/login/<user_id>/<user_name>', methods=['POST', 'GET'])
def user_login(user_id, user_name):
    """ GET Server Status API endpoint
        Args:
        Returns:
            dict: A JSON object containing the nfvacc server status information
    """
    print(USERS)
    print(str(user_id))
    name = user_name
    registered = False
    for user in USERS:
        if user.get('user_id') == str(user_id):
            print('user already exists')
            name = user.get('name')
            registered = True

    block = ''
    buttons = []
    message = ''
    button_title = ''

    if registered:
        message = 'Hi again {}. How are you today? What would you like to do?'.format(name)
        block = 'Edit Companies'
        button_title = 'Edit Companies'
        button_dict_tmpl = {
            "type": "show_block",
            "block_name": block,
            "title": button_title
        }
        buttons.append(button_dict_tmpl)
        block = 'Initializition'
        button_title = 'Continue as a guest'
        button_dict_tmpl = {
            "type": "show_block",
            "block_name": block,
            "title": button_title
        }
        buttons.append(button_dict_tmpl)
    else:
        print('first time loging in')
        message = 'Hi {}! Nice to see you. ' \
                  'I am the Scrader Bot. ' \
                  'My job is to utilize powerful machine ' \
                  'learning algorithms to extract the latest company ' \
                  'insights from news articles for a valuable ' \
                  'head start in your trading strategy. ' \
                  'I am still in development mode so many functions are not stable just yet. ' \
                  'Please subscribe in order to get notified when I will be fully functional'.format(name)

        block = 'Subscribe'
        button_title = 'Subscribe'
        button_dict_tmpl = {
            "type": "show_block",
            "block_name": block,
            "title": button_title
        }
        buttons.append(button_dict_tmpl)
        block = 'Initializition'
        button_title = 'I am just a guest'
        button_dict_tmpl = {
            "type": "show_block",
            "block_name": block,
            "title": button_title
        }
        buttons.append(button_dict_tmpl)

    response_data = {

        "messages": [
            {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "button",
                        "text": message,
                        "buttons": buttons
                    }
                }
            }
        ]
    }

    print(response_data)
    status = 200 if response_data is not None else 403
    js = json.dumps(response_data, indent=2)
    return flask.Response(js,
                          status=status,
                          mimetype='application/json')


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


@app.route('/subscribe/<user_id>/<user_name>', methods=['POST'])
def subscribe(user_id, user_name):
    """ GET Server Status API endpoint
        Args:
        Returns:
            dict: A JSON object containing the nfvacc server status information
    """
    data = request.data
    print(data)
    user_dict = {
            'user_id': str(user_id),
            'name': user_name
        }
    USERS.append(user_dict)
    response_data = {}
    status = 200 if response_data is not None else 403
    js = json.dumps(response_data, indent=2)
    return flask.Response(js,
                          status=status,
                          mimetype='application/json')


@app.route('/scrader/user_companies', methods=['POST'])
def user_data():
    """ GET Server Status API endpoint
        Args:
        Returns:
            dict: A JSON object containing the nfvacc server status information
    """

    data = flask.request.get_json()
    #print(data)

    user_name = data.get('user')
    for user in USERS:
        if user.get('name') == user_name:
            user['companies'] = data.get('companies')

    #print(USERS)

    response_data = {}
    status = 200 if response_data is not None else 403
    js = json.dumps(response_data, indent=2)
    return flask.Response(js,
                          status=status,
                          mimetype='application/json')


@app.route('/companies/<user_name>', methods=['GET'])
def user_companies(user_name):
    """ GET Server Status API endpoint
        Args:
        Returns:
            dict: A JSON object containing the nfvacc server status information
    """

    message = "Mr {} these are your selected companies".format(user_name)
    #print(USERS)
    #print(str(user_name))
    for user in USERS:
        print((str(user.get('name'))))
        if str(user.get('name')) == str(user_name):
            companies = user.get('companies')

    company_dict_tmpl = {
                        "type": "show_block",
                        "block_name": "Company Specific News",
                        "title": ""
                    }
    buttons = []
    for company in companies:
        company_dict = copy.deepcopy(company_dict_tmpl)
        company_dict["title"] = str(company)
        #print(company)
        #print(company_dict)
        buttons.append(company_dict)

    response_data = {

        "messages": [
            {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "button",
                        "text": message,
                        "buttons": buttons
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


@app.route('/user_notification/<user_id>/<time_frame>'.format(methods=['GET']))
def user_notification(user_id, time_frame):
    """ GET Server Status API endpoint
        Args:
        Returns:
            dict: A JSON object containing the nfvacc server status information
    """
    #print(user_id)
    #print(time_frame)

    user_name = user_id
    for user in USERS:
        if user.get('user_id') == user_id:
            user_name = user.get('name')

    if time_frame == 'Daily':
        message = "Mr {} you will be notified {}".format(user_name, time_frame)
        response_data = {

            "messages": [
                {"text": message}
            ]

        }
    else:
        # message = "Mr {} you can be notified for the following {}".format(user_name, time_frame)
        # response_data = {
        #     "set_attributes":
        #         {
        #             "news_type": "all"
        #         },
        #     "messages": [
        #         {
        #             "attachment": {
        #                 "type": "template",
        #                 "payload": {
        #                     "template_type": "button",
        #                     "text": message,
        #                     "buttons": [
        #                         {
        #                             "type": "show_block",
        #                             "block_name": "Company Specific News",
        #                             "title": "Instagram"
        #                         },
        #                         {
        #                             "type": "show_block",
        #                             "block_name": "Company Specific News",
        #                             "title": "VMware"
        #                         },
        #                         {
        #                             "type": "show_block",
        #                             "block_name": "Company Specific News",
        #                             "title": "IBM"
        #                         }
        #                     ]
        #                 }
        #             }
        #         },
        #         {
        #             "attachment": {
        #                 "type": "template",
        #                 "payload": {
        #                     "template_type": "button",
        #                     "text": "...",
        #                     "buttons": [
        #                         {
        #                             "type": "show_block",
        #                             "block_name": "Company Specific News",
        #                             "title": "Apple"
        #                         },
        #                         {
        #                             "type": "show_block",
        #                             "block_name": "Company Specific News",
        #                             "title": "Amazon"
        #                         },
        #                         {
        #                             "type": "show_block",
        #                             "block_name": "Company Specific News",
        #                             "title": "Adidas"
        #                         }
        #                     ]
        #                 }
        #             }
        #         },
        #         {
        #             "attachment": {
        #                 "type": "template",
        #                 "payload": {
        #                     "template_type": "button",
        #                     "text": "...",
        #                     "buttons": [
        #                         {
        #                             "type": "show_block",
        #                             "block_name": "Company Specific News",
        #                             "title": "Facebook"
        #                         },
        #                         {
        #                             "type": "show_block",
        #                             "block_name": "Company Specific News",
        #                             "title": "Google"
        #                         },
        #                         {
        #                             "type": "show_block",
        #                             "block_name": "Company Specific News",
        #                             "title": "Hooli"
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
              "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "generic",
                    "elements": [
                        {
                          "title": "See scrader's supported companies",
                          "buttons": [
                            {
                              "type": "web_url",
                              "url": "http://146.185.138.240/scrader/companies/{}".format(user_id),
                              "title": "Go Now"
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


@app.route('/news/<company>/<news_type>'.format(methods=['GET']))
def get_news(company, news_type):
    """ GET Server Status API endpoint
        Args:
        Returns:
            dict: A JSON object containing the nfvacc server status information
    """

    print("Fetching {} news for {}".format(news_type, company))

    if news_type == 'positive' or news_type == 'Positive+News':

        response_data = {
            "messages": [{
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "generic",
                        "elements": [{
                            "title": "What Amazon knows: 'The war for retail will be won in groceries'",
                            "image_url": "http://i2.cdn.turner.com/money/dam/assets/170825082748-whole-foods-fresh-fruit-apples-1024x576.jpg",
                            "subtitle": "Date: 03/09/2017 14:23",
                            "item_url": "http://money.cnn.com/2017/08/25/technology/business/amazon-whole-foods-strategy/index.html",
                            "buttons": [{
                                "type": "web_url",
                                "url": "http://edition.cnn.com/",
                                "title": "CNN.COM"
                            }]
                        }, {
                            "title": "Ocado Taps Amazon's Alexa for Voice Ordering in Convenience Push",
                            "image_url": "https://assets.bwbx.io/images/users/iqjWHBFdfxIU/i4GOoR9HbhHg/v0/1000x-1.jpg",
                            "subtitle": "Date: 03/09/2017 16:59",
                            "item_url": "https://www.bloomberg.com/news/articles/2017-08-29/ocado-taps-amazon-s-alexa-for-voice-ordering-in-convenience-push",
                            "buttons": [{
                                "type": "web_url",
                                "url": "https://www.bloomberg.com/europe",
                                "title": "BLOOMBERG.COM"
                            }]
                        }]
                    }
                }
            }]
        }

    elif news_type == 'negative' or news_type == 'Negative+News':

        response_data = {
            "messages": [{
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "generic",
                        "elements": [{
                            "title": "Instagram hackers are selling user emails and phone numbers",
                            "image_url": "http://i2.cdn.turner.com/money/dam/assets/170809095225-mostly-human-instagram-1024x576.jpg",
                            "subtitle": "Date: 01/09/2017 14:23",
                            "item_url": "http://money.cnn.com/2017/09/01/technology/business/instagram-hack/index.html",
                            "buttons": [{
                                "type": "web_url",
                                "url": "http://edition.cnn.com/",
                                "title": "CNN.COM"
                            }]
                        }, {
                            "title": "How VMwares Partnership With Amazon Could End Up Backfiring",
                            "image_url": "https://assets.bwbx.io/images/users/iqjWHBFdfxIU/i0_f6jVS4j68/v1/1000x-1.jpg",
                            "subtitle": "Customers try the cloud through AWS, but Amazon has a history of competing with its best partners.",
                            "item_url": "https://www.bloomberg.com/news/articles/2017-09-01/how-vmware-s-partnership-with-amazon-could-end-up-backfiring",
                            "buttons": [{
                                "type": "web_url",
                                "url": "https://www.bloomberg.com/europe",
                                "title": "BLOOMBERG.COM"
                            }]
                        }]
                    }
                }
            }]
        }

    else:
        response_data = {
            "messages": [{
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "generic",
                        "elements": [{
                            "title": "SAP & IBM Jointly Offer Solution for Retail, Packaged Goods",
                            "image_url": "https://staticx-tuner.zacks.com/images/default_article_images/default16.jpg",
                            "subtitle": "Enterprise application software, SAP SE ...",
                            "item_url": "https://www.zacks.com/stock/news/273394/sap-amp-ibm-jointly-offer-solution-for-retail-packaged-goods?cid=CS-CNN-HL-273394",
                            "buttons": [{
                                "type": "web_url",
                                "url": "http://edition.cnn.com/",
                                "title": "CNN.COM"
                            }]
                        }, {
                            "title": "Lenovo Shares Could Fall Another 27%: Top-Ranked Analyst",
                            "image_url": "https://assets.bwbx.io/images/users/iqjWHBFdfxIU/i0_f6jVS4j68/v1/1000x-1.jpg",
                            "subtitle": "Lenovo Group Ltd., which breathed new life into IBM's personal-computer business...",
                            "item_url": "https://www.bloomberg.com/news/articles/2017-08-21/top-ranked-analyst-says-lenovo-could-fall-another-27-percent",
                            "buttons": [{
                                "type": "web_url",
                                "url": "https://www.bloomberg.com/europe",
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


@app.route('/guest_companies/<stocks_type>'.format(methods=['GET']))
def get_companies(stocks_type):
    """ GET Server Status API endpoint
        Args:
        Returns:
            dict: A JSON object containing the nfvacc server status information
    """
    print("Fetching companies with {}.".format(stocks_type))

    if stocks_type == 'Positive+News':

        response_data = {
            "set_attributes":
                {
                    "news_type": "positive"
                },
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
                                    "block_name": "Company News",
                                    "title": "Amazon"
                                },
                                {
                                    "type": "show_block",
                                    "block_name": "Company News",
                                    "title": "Apple"
                                },
                                {
                                    "type": "show_block",
                                    "block_name": "Company News",
                                    "title": "Adidas"
                                }
                            ]
                        }
                    }
                }
            ]
        }

        # response_data = {
        #     "set_attributes":
        #         {
        #             "news_type": "positive"
        #         },
        #     "messages": [{
        #         "attachment": {
        #             "type": "template",
        #             "payload": {
        #                 "template_type": "list",
        #                 "top_element_style": "compact",
        #                 "elements": [{
        #                     "title": "Amazon",
        #                     "buttons": [{
        #                         "type": "show_block",
        #                         "block_name": "Company News",
        #                         "title": "Amazon"
        #                     }]
        #                 }, {
        #                     "title": "Apple",
        #                     "buttons": [{
        #                         "type": "show_block",
        #                         "block_name": "Company News",
        #                         "title": "Apple"
        #                     }]
        #                 },
        #                 {
        #                     "title": "Adidas",
        #                     "buttons": [{
        #                         "type": "show_block",
        #                         "block_name": "Company News",
        #                         "title": "Adidas"
        #                     }]
        #                 },
        #                 {
        #                     "title": "Facebook",
        #                     "buttons": [{
        #                         "type": "show_block",
        #                         "block_name": "Company News",
        #                         "title": "Facebook"
        #                     }]
        #                 }
        #                 ]
        #             }
        #         }
        #     }]
        # }

    elif stocks_type == 'Negative+News':

        response_data = {
            "set_attributes":
                {
                    "news_type": "negative"
                },
            "messages": [
                {
                    "attachment": {
                        "type": "template",
                        "payload": {
                            "template_type": "button",
                            "text": "These are today's top negative stocks",
                            "buttons": [
                                {
                                    "type": "show_block",
                                    "block_name": "Company News",
                                    "title": "Instagram"
                                },
                                {
                                    "type": "show_block",
                                    "block_name": "Company News",
                                    "title": "VMware"
                                }
                            ]
                        }
                    }
                }
            ]
        }

    else:

        response_data = {
            "set_attributes":
                {
                    "news_type": "all"
                },
            "messages": [
                {
                    "attachment": {
                        "type": "template",
                        "payload": {
                            "template_type": "button",
                            "text": "These are scrader's supported stocks",
                            "buttons": [
                                {
                                    "type": "show_block",
                                    "block_name": "Company Specific News",
                                    "title": "Instagram"
                                },
                                {
                                    "type": "show_block",
                                    "block_name": "Company Specific News",
                                    "title": "VMware"
                                },
                                {
                                    "type": "show_block",
                                    "block_name": "Company Specific News",
                                    "title": "IBM"
                                }
                            ]
                        }
                    }
                },
                {
                    "attachment": {
                        "type": "template",
                        "payload": {
                            "template_type": "button",
                            "text": "...",
                            "buttons": [
                                {
                                    "type": "show_block",
                                    "block_name": "Company Specific News",
                                    "title": "Apple"
                                },
                                {
                                    "type": "show_block",
                                    "block_name": "Company Specific News",
                                    "title": "Amazon"
                                },
                                {
                                    "type": "show_block",
                                    "block_name": "Company Specific News",
                                    "title": "Adidas"
                                }
                            ]
                        }
                    }
                },
                {
                    "attachment": {
                        "type": "template",
                        "payload": {
                            "template_type": "button",
                            "text": "...",
                            "buttons": [
                                {
                                    "type": "show_block",
                                    "block_name": "Company Specific News",
                                    "title": "Facebook"
                                },
                                {
                                    "type": "show_block",
                                    "block_name": "Company Specific News",
                                    "title": "Google"
                                },
                                {
                                    "type": "show_block",
                                    "block_name": "Company Specific News",
                                    "title": "Hooli"
                                }
                            ]
                        }
                    }
                }
            ]
        }

    print(response_data)
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

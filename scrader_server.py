from __future__ import print_function
import flask
import json
import math
import collections
from flask.ext.cors import CORS
from flask import request
import os
import signal
import copy
import config
import websites
import logging
import mongo
import utils

DEBUG = not False  # Enable this to print python crashes and exceptions

app = flask.Flask(__name__, static_url_path='/static')

# Make cross-origin AJAX possible (for all domains on all routes)
CORS(app, resources={r"*": {"origins": "*"}})

USERS = {}
NEXT = 0


@app.route('/scrader/companies/<user_id>'.format(methods=['GET']))
def get_companies_html(user_id):
    """ GET Server Status API endpoint
        Args:
        Returns:
            dict: A JSON object containing the nfvacc server status information
    """
    first_name = "None"
    user = USERS.get(user_id, None)
    if user is not None:
        last_name = user.get('name')
        first_name = user.get('first_name', last_name)

    return flask.render_template('companies.html', name=first_name, user_id=user_id)


@app.route('/scrader/datetime/<user_id>'.format(methods=['GET']))
def get_datetime_html(user_id):
    """ GET Server Status API endpoint
        Args:
        Returns:
            dict: A JSON object containing the nfvacc server status information
    """
    first_name = "None"
    user = USERS.get(user_id, None)
    if user is not None:
        last_name = user.get('name')
        first_name = user.get('first_name', last_name)

    return flask.render_template('new_time.html', name=first_name, user_id=user_id)


@app.route('/scrader/websites/<user_id>'.format(methods=['GET']))
def get_websites_html(user_id):
    """ GET Server Status API endpoint
        Args:
        Returns:
            dict: A JSON object containing the nfvacc server status information
    """
    first_name = "None"
    user = USERS.get(user_id, None)
    if user is not None:
        last_name = user.get('name')
        first_name = user.get('first_name', last_name)

    return flask.render_template('websites.html', name=first_name, user_id=user_id)


@app.route('/scrader/all_companies'.format(methods=['GET']))
def get_all_companies():
    """ GET Server Status API endpoint
        Args:
        Returns:
            dict: A JSON object containing the nfvacc server status information
    """

    response_data = utils.get_all_companies()

    status = 200 if response_data is not None else 403
    js = json.dumps(response_data, indent=2)
    return flask.Response(js, status=status, mimetype='application/json')


@app.route('/scrader/search_company'.format(methods=['GET']))
def company_search():
    """ GET Server Status API endpoint
        Args:
        Returns:
            dict: A JSON object containing the nfvacc server status information
    """

    company_typed = (request.args.get('last user freeform input')).lower()
    first_name = request.args.get('first name')
    user_id = request.args.get('chatfuel user id')

    user = USERS.get(user_id, None)
    if user is not None:
        user.pop('request', None)

    # print(user_id)
    company_found = utils.company_typed_search(company_typed)
    if company_found is not None:
        if company_typed != company_found.lower():
            response_data = {
                "messages": [{
                    "text":
                    "Did you mean {}?".format(company_found),
                    "quick_replies": [{
                        "title":
                        "Yes",
                        "url":
                        'http://146.185.138.240/company_specific/{}/{}'.format(
                            company_found, user_id),
                        "type":
                        "json_plugin_url"
                    }, {
                        "title": "Not really...",
                        "block_names": ["Default"]
                    }]
                }]
            }

        else:
            return specific_company(company_found, user_id)

    else:
        buttons = []

        message = "I am sorry {}. I couldn't find any match for your " \
                  "request. You could try one of the following options " \
                  "or type any company name to search into our database.".format(first_name)

        block = 'Companies'
        button_title = 'Positive News'
        button_dict_tmpl = {
            "type": "show_block",
            "block_name": block,
            "title": button_title
        }
        buttons.append(button_dict_tmpl)

        block = 'Companies'
        button_title = 'Negative News'
        button_dict_tmpl = {
            "type": "show_block",
            "block_name": block,
            "title": button_title
        }
        buttons.append(button_dict_tmpl)

        response_data = {
            "messages": [{
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "button",
                        "text": message,
                        "buttons": buttons
                    }
                }
            }]
        }

    status = 200 if response_data is not None else 403
    js = json.dumps(response_data, indent=2)
    return flask.Response(js, status=status, mimetype='application/json')


@app.route('/scrader/all_websites'.format(methods=['GET']))
def get_all_websites():
    """ GET Server Status API endpoint
        Args:
        Returns:
            dict: A JSON object containing the nfvacc server status information
    """

    response_data = websites.all_websites

    status = 200 if response_data is not None else 403
    js = json.dumps(response_data, indent=2)
    return flask.Response(js, status=status, mimetype='application/json')


@app.route('/login/<user_id>/<user_name>', methods=['POST', 'GET'])
def user_login(user_id, user_name):
    """ GET Server Status API endpoint
        Args:
        Returns:
            dict: A JSON object containing the nfvacc server status information
    """
    name = user_name
    registered = False
    first_time = True

    user = USERS.get(user_id, None)
    if user is not None:
        first_time = False
        first_name = user.get('first_name')
        if user.get('subscribed'):
            registered = True

    else:
        user_dict = {
            'first_name': user_name,
            'subscribed': False
        }
        USERS[user_id] = user_dict

    cursor = mongo.find_matches('users', {"user_id": user_id})
    print(mongo.find_one_match('users', {"user_id": user_id}))
    if cursor.count() == 0:
        col_dict = {
            'first_name': user_name,
            'subscribed': False,
            'user_id': user_id
        }
        mongo.insert_one('users', col_dict)
        # for document in cursor:
        #     print(document)
    else:
        for document in cursor:
            print(document)
        first_time = False
        first_name = next(item['first_name'] for item in cursor)
        for doc in cursor:
            first_name = doc.get('first_name')
            if doc.get('subscribed'):
                registered = True

    buttons = []

    if first_time:
        # print('first time loging in')
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
    else:
        block = 'Companies'
        button_title = 'Positive News'
        button_dict_tmpl = {
            "type": "show_block",
            "block_name": block,
            "title": button_title
        }
        buttons.append(button_dict_tmpl)

        block = 'Companies'
        button_title = 'Negative News'
        button_dict_tmpl = {
            "type": "show_block",
            "block_name": block,
            "title": button_title
        }
        buttons.append(button_dict_tmpl)

        if registered:
            message = 'Hi again {}. What would you like me to show you? ' \
                      'Remember you can type any company you want to search for scraped news'.format(first_name)

            pref_button = {
                "type": "show_block",
                "block_name": "Preferences",
                "title": "Edit Preferences"
            }
            buttons.append(pref_button)
        else:
            message = 'Hi again {}. What would you like me to show you? ' \
                      'Remember you can type any company you want to search for scraped news'.format(name)

            block = 'Subscribe'
            button_title = 'Subscribe'
            button_dict_tmpl = {
                "type": "show_block",
                "block_name": block,
                "title": button_title
            }
            buttons.append(button_dict_tmpl)

    response_data = {
        "messages": [{
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "button",
                    "text": message,
                    "buttons": buttons
                }
            }
        }]
    }

    # print(response_data)
    status = 200 if response_data is not None else 403
    js = json.dumps(response_data, indent=2)
    return flask.Response(js, status=status, mimetype='application/json')


@app.route(
    '/subscribe/<user_id>/<user_last_name>/<user_first_name>',
    methods=['POST'])
def subscribe(user_id, user_last_name, user_first_name):
    """ GET Server Status API endpoint
        Args:
        Returns:
            dict: A JSON object containing the nfvacc server status information
    """

    cursor = mongo.find_matches('users', {"user_id": user_id})
    if cursor.count() > 0:
        # for document in cursor:
        #     print(document)
        mongo.insert_one_in('users', {"user_id": user_id}, {'name': user_last_name})
        mongo.insert_one_in('users', {"user_id": user_id}, {'subscribed': True})

    user = USERS.get(user_id, None)
    if user is not None:
        user['name'] = user_last_name
        user['subscribed'] = True


    response_data = {}
    status = 200 if response_data is not None else 403
    js = json.dumps(response_data, indent=2)
    return flask.Response(js, status=status, mimetype='application/json')


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
    return flask.Response(js, status=status, mimetype='application/json')


@app.route('/scrader/user_companies', methods=['POST'])
def user_companies_data():
    """ GET Server Status API endpoint
        Args:
        Returns:
            dict: A JSON object containing the nfvacc server status information
    """

    data = flask.request.get_json()

    user_id = data.get('user')
    user = USERS.get(user_id, None)
    if user is not None:
        user['companies'] = data.get('companies')
        user['notification_type'] = 'Companies'

    response_data = {}
    status = 200 if response_data is not None else 403
    js = json.dumps(response_data, indent=2)
    return flask.Response(js, status=status, mimetype='application/json')


@app.route('/scrader/user_datetime', methods=['POST'])
def user_datetime_data():
    """ GET Server Status API endpoint
        Args:
        Returns:
            dict: A JSON object containing the nfvacc server status information
    """

    data = flask.request.get_json()
    user_id = data.get('user')
    user = USERS.get(user_id, None)
    if user is not None:
        user['datetime'] = data.get('datetime')

    response_data = {}
    status = 200 if response_data is not None else 403
    js = json.dumps(response_data, indent=2)
    return flask.Response(js, status=status, mimetype='application/json')


@app.route('/scrader/user_datetime/<user_id>', methods=['GET'])
def get_user_datetime_data(user_id):
    """ GET Server Status API endpoint
        Args:
        Returns:
            dict: A JSON object containing the nfvacc server status information
    """

    user = USERS.get(user_id, None)
    datetime = ''
    if user is not None:
        datetime = user.get('datetime', '')

    response_data = datetime
    status = 200 if response_data is not None else 403
    js = json.dumps(response_data, indent=2)
    return flask.Response(js, status=status, mimetype='application/json')


@app.route('/scrader/modify_user/<user_id>/<company_name>/<action>', methods=['GET'])
def modify_user_companies(user_id, company_name, action):
    """ GET Server Status API endpoint
        Args:
        Returns:
            dict: A JSON object containing the nfvacc server status information
    """

    response_data = {}
    user = USERS.get(user_id, None)
    if user is not None:
        user_name = user.get('first_name')
        if action == 'add':
            user['companies'].append(company_name)
            message = "{} now on you will be notified for {} too.".format(user_name, company_name)
        else:
            user['companies'].remove(company_name)
            message = "{} now on you won't be notified for {}.".format(user_name, company_name)

        response_data = {"messages": [{"text": message}]}

    # print(response_data)
    status = 200 if response_data is not None else 403
    js = json.dumps(response_data, indent=2)
    return flask.Response(js, status=status, mimetype='application/json')


@app.route('/scrader/user_websites', methods=['POST'])
def user_websites_data():
    """ GET Server Status API endpoint
        Args:
        Returns:
            dict: A JSON object containing the nfvacc server status information
    """

    data = flask.request.get_json()

    user_id = data.get('user')
    user = USERS.get(user_id, None)
    if user is not None:
        user['websites'] = data.get('websites')

    response_data = {}
    status = 200 if response_data is not None else 403
    js = json.dumps(response_data, indent=2)
    return flask.Response(js, status=status, mimetype='application/json')


@app.route('/companies/<user_id>', methods=['GET'])
def user_companies(user_id):
    """ GET Server Status API endpoint
        Args:
        Returns:
            dict: A JSON object containing the nfvacc server status information
    """

    subscribed_companies = []
    user = USERS.get(user_id, None)
    if user is not None:
        subscribed_companies = user.get('companies', [])

    # print(subscribed_companies)
    response_data = subscribed_companies
    status = 200 if response_data is not None else 403
    js = json.dumps(response_data, indent=2)
    return flask.Response(js, status=status, mimetype='application/json')


@app.route('/websites/<user_id>', methods=['GET'])
def user_websites(user_id):
    """ GET Server Status API endpoint
        Args:
        Returns:
            dict: A JSON object containing the nfvacc server status information
    """

    subscribed_websites = []
    user = USERS.get(user_id, None)
    if user is not None:
        subscribed_websites = user.get('websites', [])

    response_data = subscribed_websites
    status = 200 if response_data is not None else 403
    js = json.dumps(response_data, indent=2)
    return flask.Response(js, status=status, mimetype='application/json')


@app.route('/user_notification/<user_id>/<time_frame>'.format(methods=['GET']))
def user_notification(user_id, time_frame):
    """ GET Server Status API endpoint
        Args:
        Returns:
            dict: A JSON object containing the nfvacc server status information
    """

    user = USERS.get(user_id, None)
    user_name = user.get('first_name', user_id)

    if time_frame == 'Daily':

        user['notification_type'] = 'Daily'
        message = "{} you will be notified {}".format(user_name, time_frame)
        response_data = {"messages": [{"text": message}]}
    else:

        user['notification_type'] = 'Companies'
        response_data = {
            "messages": [{
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type":
                        "generic",
                        "elements": [{
                            "title":
                            "See scrader's supported companies",
                            "buttons": [{
                                "type":
                                "web_url",
                                "url":
                                "http://146.185.138.240/scrader/companies/{}".
                                format(user_id),
                                "title":
                                "Go Now"
                            }]
                        }]
                    }
                }
            }]
        }

    status = 200 if response_data is not None else 403
    js = json.dumps(response_data, indent=2)
    return flask.Response(js, status=status, mimetype='application/json')


@app.route('/user_daily_notification/<user_id>'.format(methods=['GET']))
def user_daily_notification(user_id):
    """ GET Server Status API endpoint
        Args:
        Returns:
            dict: A JSON object containing the nfvacc server status information
    """

    user = USERS.get(user_id, None)
    datetime = user.get('datetime')

    message = 'You will be notified daily @ {}. You can also' \
              ' be notified whenever companies you choose appear on our feed.'.format(datetime)

    buttons = []
    block = 'News'
    button_title = "Today's News"
    button_dict_tmpl = {
        "type": "show_block",
        "block_name": block,
        "title": button_title
    }
    buttons.append(button_dict_tmpl)

    extra_button = {}
    extra_button['type'] = "web_url"
    extra_button['title'] = 'Select Companies'
    extra_button['url'] = "http://146.185.138.240/scrader/companies/{}".format(user_id)
    buttons.append(extra_button)

    response_data = {
        "messages": [
            {"text": message},
            {"attachment": {
                "type": "template",
                "payload": {
                    "template_type":
                        "button",
                    "text":
                        "Now how would you like to continue?",
                    "buttons": buttons
                }
            }
        }]
    }

    status = 200 if response_data is not None else 403
    js = json.dumps(response_data, indent=2)
    return flask.Response(js, status=status, mimetype='application/json')


@app.route('/company_specific/<company>/<user_id>'.format(methods=['GET']))
def specific_company(company, user_id):
    """ GET Server Status API endpoint
        Args:
        Returns:
            dict: A JSON object containing the nfvacc server status information
    """

    subscribed = False
    followed = False
    user_request = None
    user = USERS.get(user_id, None)
    if user is not None:
        if user.get('notification_type') == 'Companies':
            subscribed = True
            if company in user.get('companies'):
                followed = True
        user_request = user.get('request', None)

    extra_button = {}
    # if followed:
    #     extra_button['type'] = "json_plugin_url"
    #     extra_button['title'] = 'Unfollow'
    #     extra_button['url'] = "http://146.185.138.240/scrader/modify_user/{}/{}/remove".format(user_id,company)
    # else:
    if subscribed:
        if not followed:
            extra_button['type'] = "json_plugin_url"
            extra_button['title'] = 'Follow'
            extra_button['url'] = "http://146.185.138.240/scrader/modify_user/{}/{}/add".format(user_id,company)

    company_given = company
    type_of_news = utils.company_news_type(company_given)

    if type_of_news:
        # print(type_of_news)
        one_news_type = True
        if len(type_of_news) > 1:
            type_of_news.sort(reverse=True)
            one_news_type = False

        # print(type_of_news)
        news_buttons = []
        for news_type in type_of_news:
            if news_type == 'good_companies':
                new_button = {
                    "type": "show_block",
                    "block_names": ["Fetch news"],
                    "title": "Positive News"
                }
                news_buttons.append(new_button)
            else:
                new_button = {
                    "type": "show_block",
                    "block_names": ["Fetch news"],
                    "title": "Negative News"
                }
                news_buttons.append(new_button)

        if extra_button:
            if one_news_type:
                arg = new_button.get('title').split()[0]
                return helper_function(extra_button, company, arg.lower())

        indication_message = {}
        if not one_news_type:
            if user_request is not None:
                if user_request == 'Positive+News':
                    user_request = 'negative'
                else:
                    user_request = 'positive'
                indication_message = {"text": 'There are also {} news for {}'.format(user_request, company)}

        # print(news_buttons)
        response_data = {
            "set_attributes": {
                "company_requested": company
            },
            "messages": [{
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type":
                        "button",
                        "text":
                        "Which news would you like to see about {}?".format(
                            company),
                        "buttons": news_buttons
                    }
                }
            }]
        }

        if extra_button:
            response_data['messages'][0]['attachment']['payload']['buttons'].append(extra_button)
        else:
            if one_news_type:
                title_butt = news_buttons[0]['title'].split()
                news_type = title_butt[0].lower()
                return get_news(company, news_type, 1)

        if indication_message:
            response_data['messages'].insert(0,indication_message)

    else:
        negative_message = {"text": 'No articles found for {}'.format(company)}
        response_data = {
            "set_attributes": {
                "company_requested": company
            },
            "messages": [negative_message]
        }
        if extra_button:
            extra_message = {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type":
                            "button",
                        "text":
                            "Remember you can {} {}.".format(extra_button.get('title').lower(), company),
                        "buttons": [extra_button]
                    }
                }
            }
            response_data['messages'].append(extra_message)


    status = 200 if response_data is not None else 403
    js = json.dumps(response_data, indent=2)
    return flask.Response(js, status=status, mimetype='application/json')


def helper_function(extra_button, company, news_type):

    message = {
        "attachment": {
            "type": "template",
            "payload": {
            "template_type": "button",
            "text": "Remember you can follow {}".format(company),
            "buttons": [
                extra_button
            ]
            }
        }
    }

    return get_news(company, news_type, message)


@app.route('/news/<company>/<news_type>/<page_num>'.format(methods=['GET']))
def get_news(company, news_type, page_num):
    """ GET Server Status API endpoint
        Args:
        Returns:
            dict: A JSON object containing the nfvacc server status information
    """

    # print(
    #     "Fetching {} news for {} page {}".format(news_type, company, page_num))

    extra_message = {}
    if isinstance(page_num, dict):
        extra_message = page_num
        page_num = 1

    elements = []
    element = {
        "title": '',
        "image_url": '',
        "subtitle": '',
        "item_url": '',
        "buttons": [{
            "type": "web_url",
            "url": '',
            "title": ''
        }]
    }

    messages = []
    message = {
        "attachment": {
            "type": "template",
            "payload": {
                "template_type": "generic",
                "elements": elements
            }
        }
    }

    quick_replies = []
    quick_reply = {"title": '', "url": '', "type": "json_plugin_url"}

    if news_type == 'positive' or news_type == 'Positive+News':
        news_message = 'Positive'
        direction = 'POS'
    else:
        direction = 'NEG'
        news_message = 'Negative'


    # requested_news = utils.get_news_by_direction(direction)
    requested_news = utils.get_news_by_direction_and_company(direction, company)
    # print(requested_news)

    f = lambda A, n=3: [A[i:i + n] for i in range(0, len(A), n)]
    news_per_page = f(requested_news)
    # print(news_per_page)
    news_to_show = news_per_page[int(page_num) - 1]
    # print(news_to_show)
    all_quick_replies_page_numbers = [
        i + 1 for i, _ in enumerate(news_per_page)
    ]
    # print(all_quick_replies_page_numbers)
    quick_replies_page_numbers_to_show = filter(lambda x: x != int(page_num),
                                                all_quick_replies_page_numbers)
    # print(quick_replies_page_numbers_to_show)

    for new in news_to_show:
        element = copy.deepcopy(element)
        element['title'] = new.get('title')[0:79]
        element['image_url'] = str(new.get('image_url'))
        element['subtitle'] = new.get('subtitle')
        element['item_url'] = str(new.get('item_url'))
        element['buttons'][0]['url'] = new.get('website_url')
        element['buttons'][0]['title'] = new.get('website')
        elements.append(element)

    for page_number in quick_replies_page_numbers_to_show:
        quick_reply = copy.deepcopy(quick_reply)
        quick_reply['title'] = "Page {}".format(page_number)
        quick_reply['url'] = "http://146.185.138.240/news/{}/{}/{}".format(
            company, news_type, page_number)
        quick_replies.append(quick_reply)

    if quick_replies:
        message['quick_replies'] = quick_replies

    message['attachment']['payload']['elements'] = elements

    article = 'articles' if len(requested_news) > 1 else 'article'
    top_message = {"text": '{} {} {} found for {}'.format(len(requested_news), news_message, article, company)}

    if extra_message:
        messages.append(extra_message)

    if int(page_num) == 1:
        messages.append(top_message)

    # print(message)
    messages.append(message)

    response_data = {"messages": messages}

    # print(response_data)
    status = 200 if response_data is not None else 403
    js = json.dumps(response_data, indent=2)
    return flask.Response(js, status=status, mimetype='application/json')


@app.route('/guest_companies/<stocks_type>'.format(methods=['GET']))
def get_companies(stocks_type):
    """ GET Server Status API endpoint
        Args:
        Returns:
            dict: A JSON object containing the nfvacc server status information
    """

    global NEXT
    NEXT = 0 if request.args.get('NEXT') is not None else NEXT
    user_id = request.args.get('chatfuel user id')
    user = USERS.get(user_id, None)
    if user is not None:
        user['request'] = stocks_type

    # print(user)
    # print("Fetching companies with {}.".format(stocks_type))
    total_articles = utils.total_articles()

    attributes_dict = {"news_type": '', "stocks_type": ''}

    element = {
        "title": '',
        "image_url": '',
        "subtitle": '',
        "buttons": [{
            "type": "json_plugin_url",
            "url": '',
            "title": ''
        }]
    }
    messages = [{
        "attachment": {
            "type": "template",
            "payload": {
                "template_type": "list",
                "top_element_style": "compact",
                "elements": []
            }
        }
    }]
    next_button = {
        "type": "show_block",
        "block_name": "Next Company",
        "title": ''
    }

    if stocks_type == 'Positive+News':
        companies_type = 'good_companies'
        news_type = 'positive'

    else:
        companies_type = 'bad_companies'
        news_type = 'negative'

    requested_companies = utils.companies_by_type(companies_type)
    requested_companies = reorder_companies(requested_companies, user_id)
    four_packets = math.ceil((len(requested_companies) / 4.0))
    attributes_dict['news_type'] = news_type
    attributes_dict['stocks_type'] = stocks_type
    start = NEXT * 4
    for index, company in enumerate(requested_companies[start:]):
        if index < 4 :
            element = copy.deepcopy(element)
            name_net = company.get('company_name').split()[0]
            element['title'] = company.get('company_name')
            element['image_url'] = company.get('company_logo')
            company_number_of_artcles = len(company.get('company_news_ids'))
            if company_number_of_artcles == 1:
                article = utils.get_article_by_id(company.get('company_news_ids')[0])
                article_title = article.get('title')[0:79]
            element['subtitle'] = \
                "{} out of {} articles".format(company_number_of_artcles,
                                                   total_articles)\
                    if company_number_of_artcles > 1 else article_title
            element['buttons'][0][
                'title'] = 'View articles' if company_number_of_artcles > 1 else 'View article'
            element['buttons'][0][
                'url'] = 'http://146.185.138.240/company_specific/{}/{}'.format(
                    name_net, user_id)
            messages[0]['attachment']['payload']['elements'].append(
                element)

    response_data = {
        'set_attributes': attributes_dict,
        'messages': messages
    }

    if four_packets > 1:
        if (NEXT + 2) <= four_packets:
            remaining = len(requested_companies) - (NEXT + 1) * 4
            next_button['title'] = "Next {}/{}".format(
                remaining, len(requested_companies))
            response_data['messages'][0]['attachment']['payload'][
                'buttons'] = [next_button]

    if len(response_data['messages'][0]['attachment']['payload']['elements']) == 1:
        response_data['messages'][0]['attachment']['payload']['template_type'] = 'generic'
        response_data['messages'][0]['attachment']['payload'].\
            pop('top_element_style', None)

    NEXT += 1
    status = 200 if response_data is not None else 403
    js = json.dumps(response_data, indent=2)
    return flask.Response(js, status=status, mimetype='application/json')


def reorder_companies(companies_list, user_id):

    user_subscibed_companies = USERS.get(user_id).get('companies', None)
    sorted_list = []
    if user_subscibed_companies is not None:
        for user_company in user_subscibed_companies:
            for company in companies_list:
                if user_company == company.get('company_name'):
                    sorted_list.append(company)
                    companies_list.remove(company)
                    break

    sorted_list.extend(companies_list)
    return sorted_list


def signal_sigint_handler(rec_signal, rec_frame):
    os._exit(1)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_sigint_handler)

    # set the flask logger => ERROR: do not print API calls

    logging.basicConfig(filename='logs.log',level=logging.INFO)
    logging.debug('This message should go to the log file')
    utils.article_from_excel()
    # utils.news_poll(10)
    utils.update_companies_news_once()
    mongo.init_database()

    app.run(host=config.HOST, port=config.PORT, debug=DEBUG)

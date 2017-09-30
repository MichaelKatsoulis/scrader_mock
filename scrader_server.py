from __future__ import print_function
import flask
import json
import math
from flask.ext.cors import CORS
from flask import request
import os
import signal
import copy
import config
import companies
import websites
import news
import logging

DEBUG = False  # Enable this to print python crashes and exceptions

app = flask.Flask(__name__, static_url_path='/static')

# Make cross-origin AJAX possible (for all domains on all routes)
CORS(app, resources={r"*": {"origins": "*"}})

USERS = []
NEXT = 0


@app.route('/scrader/companies/<user_id>'.format(methods=['GET']))
def get_companies_html(user_id):
    """ GET Server Status API endpoint
        Args:
        Returns:
            dict: A JSON object containing the nfvacc server status information
    """
    name = "None"

    for user in USERS:
        if user.get('user_id') == user_id:
            last_name = user.get('name')
            name = user.get('first_name', last_name)

    return flask.render_template('companies.html', name=name, user_id=user_id)


@app.route('/scrader/websites/<user_id>'.format(methods=['GET']))
def get_websites_html(user_id):
    """ GET Server Status API endpoint
        Args:
        Returns:
            dict: A JSON object containing the nfvacc server status information
    """
    name = "None"

    for user in USERS:
        if user.get('user_id') == user_id:
            last_name = user.get('name')
            name = user.get('first_name', last_name)

    return flask.render_template('websites.html', name=name, user_id=user_id)


@app.route('/scrader/all_companies'.format(methods=['GET']))
def get_all_companies():
    """ GET Server Status API endpoint
        Args:
        Returns:
            dict: A JSON object containing the nfvacc server status information
    """

    good_company_names = [
        company['company_name']
        for company in companies.all_companies['good_companies']
    ]
    bad_company_names = [
        company['company_name']
        for company in companies.all_companies['bad_companies']
    ]
    companies_dupl = good_company_names + bad_company_names
    response_data = list(set(companies_dupl))

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
    # print(user_id)
    company_found = company_typed_search(company_typed)
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


def company_typed_search(company_):

    company_found = None
    all_companies = companies.all_companies
    for company_type, companies_list in all_companies.items():
        for company_dict in companies_list:
            company_name = company_dict.get('company_name').split()[0]
            if company_ in company_name.lower():
                return company_name

    return company_found


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
    # print(USERS)
    name = user_name
    registered = False
    exists = False
    first_time = True

    for user in USERS:
        if user.get('user_id') == str(user_id):
            # print('user already exists')
            exists = True
            first_time = False
            first_name = user.get('first_name')
            if user.get('subscribed'):
                registered = True

    if not exists:
        user_dict = {
            'user_id': str(user_id),
            'first_name': user_name,
            'subscribed': False
        }
        USERS.append(user_dict)

    buttons = []

    if registered:
        message = 'Hi again {}. What would you like me to show you? ' \
                  'Remember you can type any company you want to search for scraped news'.format(first_name)

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

        pref_button = {
            "type": "show_block",
            "block_name": "Preferences",
            "title": "Edit Preferences"
        }
        buttons.append(pref_button)
    else:
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
        block = 'Initializition'
        button_title = 'I am just a guest'
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

    for user in USERS:
        if user.get('user_id') == str(user_id):
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

    user_name = data.get('user')
    for user in USERS:
        if user.get('first_name') == user_name:
            user['companies'] = data.get('companies')
            user['notification_type'] = 'Companies'
    response_data = {}
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
    for user in USERS:
        if user.get('user_id') == user_id:
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

    user_name = data.get('user')
    for user in USERS:
        if user.get('first_name') == user_name:
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
    for user in USERS:
        if user.get('user_id') == user_id:
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
    for user in USERS:
        if user.get('user_id') == user_id:
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

    user_name = user_id
    user_index = 0
    for ind, user in enumerate(USERS):
        if user.get('user_id') == user_id:
            user_name = user.get('first_name')
            user_index = ind

    if time_frame == 'Daily':

        USERS[user_index]['notification_type'] = 'Daily'
        message = "{} you will be notified {}".format(user_name, time_frame)
        response_data = {"messages": [{"text": message}]}
    else:

        USERS[user_index]['notification_type'] = 'Companies'
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

    for user in USERS:
        if user.get('user_id') == str(user_id):
            if user.get('notification_type') == 'Companies':
                subscribed = True
                if company in user.get('companies'):
                    followed = True
            user_request = user.get('request', None)

    extra_button = {}
    if followed:
        extra_button['type'] = "json_plugin_url"
        extra_button['title'] = 'Unfollow'
        extra_button['url'] = "http://146.185.138.240/scrader/modify_user/{}/{}/remove".format(user_id,company)
    else:
        if subscribed:
            extra_button['type'] = "json_plugin_url"
            extra_button['title'] = 'Follow'
            extra_button['url'] = "http://146.185.138.240/scrader/modify_user/{}/{}/add".format(user_id,company)

    company_given = company
    all_companies = companies.all_companies
    type_of_news = []
    for type, companies_list in all_companies.items():
        for company_dict in companies_list:
            if company_given == company_dict.get('company_name').split()[0]:
                # print('company ' + company_given + ' found in ' + type)
                type_of_news.append(type)
                break

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

    if not one_news_type:
        if user_request is not None:
            print('user requested before {}'.format(user_request))

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
            news_type = news_buttons[0]['title']
            return get_news(company, news_type, 1)

    status = 200 if response_data is not None else 403
    js = json.dumps(response_data, indent=2)
    return flask.Response(js, status=status, mimetype='application/json')


@app.route('/news/<company>/<news_type>/<page_num>'.format(methods=['GET']))
def get_news(company, news_type, page_num):
    """ GET Server Status API endpoint
        Args:
        Returns:
            dict: A JSON object containing the nfvacc server status information
    """

    print(
        "Fetching {} news for {} page {}".format(news_type, company, page_num))

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
    print(news_type)
    messages = [
        {"text": '{} news for {}'.format(news_type, company)}
    ]
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
        direction = 'good'
    else:
        direction = 'bad'

    all_news = news.news
    requested_news = [
        new for new in all_news if new.get('direction') == direction
    ]

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
        element['title'] = new.get('title')
        element['image_url'] = new.get('image_url')
        element['subtitle'] = new.get('subtitle')
        element['item_url'] = new.get('item_url')
        element['buttons'][0]['url'] = new.get('website_url')
        element['buttons'][0]['title'] = new.get('website')
        elements.append(element)

    for page_number in quick_replies_page_numbers_to_show:
        quick_reply = copy.deepcopy(quick_reply)
        quick_reply['title'] = "Page {}".format(page_number)
        quick_reply['url'] = "http://146.185.138.240/news/{}/{}/{}".format(
            company, news_type, page_number)
        quick_replies.append(quick_reply)

    message['quick_replies'] = quick_replies

    message['attachment']['payload']['elements'] = elements
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
    for user in USERS:
        if user.get('user_id') == user_id:
            user['request'] = stocks_type
    # print(user_id)
    # print("Fetching companies with {}.".format(stocks_type))
    total_articles = companies.Total_articles

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

    both = False
    if stocks_type == 'Positive+News':
        companies_type = 'good_companies'
        news_type = 'positive'

    elif stocks_type == 'Negative+News':
        companies_type = 'bad_companies'
        news_type = 'negative'
    else:
        both = True

    if not both:
        requested_companies = companies.all_companies.get(companies_type)
        four_packets = math.ceil((len(requested_companies) / 4.0))
        attributes_dict['news_type'] = news_type
        attributes_dict['stocks_type'] = stocks_type
        start = NEXT * 4
        for index, company in enumerate(requested_companies[start:]):
            # print(index)
            if index < start + 4:
                element = copy.deepcopy(element)
                name_net = company.get('company_name').split()[0]
                element['title'] = company.get('company_name')
                element['image_url'] = company.get('company_logo')
                element['subtitle'] = \
                    "{} out of {} articles".format(company.get('company_articles'),
                                                       total_articles) if company.get(
                    'company_articles') > 1 else "One article Title"
                element['buttons'][0][
                    'title'] = 'View articles' if company.get(
                        'company_articles') > 1 else 'View article'
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

    else:

        response_data = {
            "set_attributes": {
                "news_type": "all"
            },
            "messages": [{
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type":
                        "button",
                        "text":
                        "These are scrader's supported stocks",
                        "buttons": [{
                            "type": "show_block",
                            "block_name": "Company Specific News",
                            "title": "Instagram"
                        }, {
                            "type": "show_block",
                            "block_name": "Company Specific News",
                            "title": "VMware"
                        }, {
                            "type": "show_block",
                            "block_name": "Company Specific News",
                            "title": "IBM"
                        }]
                    }
                }
            }, {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type":
                        "button",
                        "text":
                        "...",
                        "buttons": [{
                            "type": "show_block",
                            "block_name": "Company Specific News",
                            "title": "Apple"
                        }, {
                            "type": "show_block",
                            "block_name": "Company Specific News",
                            "title": "Amazon"
                        }, {
                            "type": "show_block",
                            "block_name": "Company Specific News",
                            "title": "Adidas"
                        }]
                    }
                }
            }, {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type":
                        "button",
                        "text":
                        "...",
                        "buttons": [{
                            "type": "show_block",
                            "block_name": "Company Specific News",
                            "title": "Facebook"
                        }, {
                            "type": "show_block",
                            "block_name": "Company Specific News",
                            "title": "Google"
                        }, {
                            "type": "show_block",
                            "block_name": "Company Specific News",
                            "title": "Hooli"
                        }]
                    }
                }
            }]
        }

    NEXT += 1
    # print(response_data)
    status = 200 if response_data is not None else 403
    js = json.dumps(response_data, indent=2)
    return flask.Response(js, status=status, mimetype='application/json')


def signal_sigint_handler(rec_signal, rec_frame):
    os._exit(1)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_sigint_handler)

    # set the flask logger => ERROR: do not print API calls

    logging.basicConfig(filename='logs.log',level=logging.INFO)
    logging.debug('This message should go to the log file')
    logging.info('So should this')
    logging.warning('And this, too')

    app.run(host=config.HOST, port=config.PORT, debug=DEBUG)

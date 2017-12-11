import mongo


def user_login(user_name, user_id):
    name = user_name
    registered = False
    first_time = True

    user = mongo.find_one_match('users', {"user_id": user_id})
    if user is not None:
        first_time = False
        first_name = user.get('first_name')
        if user.get('subscribed'):
            registered = True
    else:
        user_dict = {
            'first_name': user_name,
            'subscribed': False,
            'user_id': user_id
        }
        mongo.insert_one('users', user_dict)

    buttons = []

    if first_time:
        # print('first time loging in')
        message = 'Hi {}! Nice to see you. ' \
                  'I am the Scrader Bot. ' \
                  'My job is to utilize powerful machine ' \
                  'learning algorithms to extract the latest company ' \
                  'insights from news articles for a valuable ' \
                  'head start in your trading strategy. ' \
                  'I am still in development mode so many functions are not ' \
                  'stable just yet. ' \
                  'Please subscribe in order to get notified when I will be ' \
                  'fully functional'.format(name)

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
                      'Remember you can type any company you want to search ' \
                      'for scraped news'.format(first_name)

            pref_button = {
                "type": "show_block",
                "block_name": "Preferences",
                "title": "Edit Preferences"
            }
            buttons.append(pref_button)
        else:
            message = 'Hi again {}. What would you like me to show you? ' \
                      'Remember you can type any company you want to search ' \
                      'for scraped news'.format(name)

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

    return response_data


def user_subscribe(user_id, user_last_name, user_first_name):
    user = mongo.find_one_match('users', {"user_id": user_id})
    if user is not None:
        mongo.insert_one_in('users', {"user_id": user_id},
                                     {'name': user_last_name})
        mongo.insert_one_in('users', {"user_id": user_id},
                                     {'subscribed': True})


def update_user_companies_data(user_id, data):
    user = mongo.find_one_match('users', {"user_id": user_id})
    if user is not None:
        mongo.insert_one_in('users', {"user_id": user_id},
                                     {'companies': data.get('companies')})
        mongo.insert_one_in('users', {"user_id": user_id},
                                     {'notification_type': 'Companies'})


def update_user_datetime_data(user_id, data):
        user = mongo.find_one_match('users', {"user_id": user_id})
        if user is not None:
            mongo.insert_one_in('users', {"user_id": user_id},
                                         {'datetime': data.get('datetime')})


def get_user_datetime_data(user_id):
    user = mongo.find_one_match('users', {"user_id": user_id})
    datetime = ''
    if user is not None:
        datetime = user.get('datetime', '')
    return datetime


def modify_user_companies(user_id, company_name, action):
    response_data = {}
    user = mongo.find_one_match('users', {"user_id": user_id})
    if user is not None:
        user_name = user.get('first_name')
        if action == 'add':
            user['companies'].append(company_name)
            message = "{} now on you will be notified for {} too.".\
                format(user_name, company_name)
        else:
            user['companies'].remove(company_name)
            message = "{} now on you won't be notified for {}.".\
                format(user_name, company_name)

        mongo.insert_one_in('users', {"user_id": user_id},
                                     {'companies': user['companies']})

        response_data = {"messages": [{"text": message}]}
        return response_data

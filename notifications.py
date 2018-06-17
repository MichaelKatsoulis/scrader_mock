import requests
import pytz
import logging
import datetime
import time
from pymongo import MongoClient


dbcli = MongoClient('127.0.0.1', 8080)
db = dbcli['scrader']
db.authenticate('scrader', 'scr@d3r')
logger = logging.getLogger('myapp')
hdlr = logging.FileHandler('notification_logs.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)


def send_user_news(user):
    logger.info("sending staff for user" + user.get('first_name'))

    if not user.get('companies'):
        return

    url = 'https://api.chatfuel.com/bots/591189a0e4b0772d3373542b/' \
          'users/{}/' \
          'send?chatfuel_token=vnbqX6cpvXUXFcOKr5RHJ7psSpHDRzO1hXBY8dkvn50ZkZyWML3YdtoCnKH7FSjC' \
          '&chatfuel_block_id=5b01b49fe4b03903064c0f64&last%20'.format(user.get('user_id'))
    try:
        requests.post(url)
    except requests.exceptions.RequestException:
        pass


if __name__ == '__main__':
    while True:
        utc = pytz.utc
        utc_time = datetime.datetime.now(utc)
        time_now = str(utc_time.now().time())
        hour = str(int(time_now.split(':')[0]))
        if int(hour) < 10:
            hour = '0' + hour

        minutes = time_now.split(':')[1]
        if int(minutes) < 10:
            minutes = '0' + minutes

        formatted_time = hour + ":" + minutes
        logger.info(formatted_time)
        users_collection = db['users']
        query = {'datetime': formatted_time}
        users = users_collection.find(query)
        for user in users:
            send_user_news(user)
        time.sleep(60)

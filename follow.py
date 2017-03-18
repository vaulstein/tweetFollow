#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import ConfigParser
import argparse
import csv
import datetime
import json
import os
import socket
import sys
import time
import urllib

import oauth2
import pytz
import requests

import settings

#from unfollow import follow_check

try:
    import tzlocal
    _DEFAULT_TIMEZONE = tzlocal.get_localzone().zone
except:
    _DEFAULT_TIMEZONE = 'Asia/Calcutta'

import six

__version__ = "1.0.dev0"


# url for list of valid timezones
_TZ_URL = 'http://en.wikipedia.org/wiki/List_of_tz_database_time_zones'


CONF = {
    'consumer_key': '',
    'consumer_secret': '',
    'api_key': '',
    'api_secret': '',
    'data_to_fetch': 1,
    'query': '',
    'geocode': '',
    'lang': '',
    'result_type': 'popular',
    'count': 100,
    'until': None,
    'since_id': None,
}

RESULT_MAP = {
    '1': 'popular',
    '2': 'recent',
    '3': 'mixed'
}


def decoding_strings(f):
    def wrapper(*args, **kwargs):
        out = f(*args, **kwargs)
        if isinstance(out, six.string_types) and not six.PY3:
            # todo: make encoding configurable?
            if six.PY3:
                return out
            else:
                return out.decode(sys.stdin.encoding)
        return out
    return wrapper


def _input_compat(prompt):
    if six.PY3:
        r = input(prompt)
    else:
        r = raw_input(prompt)
    return r

if six.PY3:
    str_compat = str
else:
    str_compat = unicode

dateObject = 'YYYY-MM-DD'


@decoding_strings
def ask(question, answer=str_compat, default=None, l=None, options=None):
    if answer == str_compat:
        r = ''
        while True:
            if default:
                r = _input_compat('> {0} [{1}] '.format(question, default))
            else:
                r = _input_compat('> {0} '.format(question, default))

            r = r.strip()

            if len(r) <= 0:
                if default:
                    r = default
                    break
                else:
                    print('You must enter something')
            else:
                if l and len(r) != l:
                    print('You must enter a {0} letters long string'.format(l))
                else:
                    break

        return r

    elif answer == bool:
        r = None
        while True:
            if default is True:
                r = _input_compat('> {0} (Y/n) '.format(question))
            elif default is False:
                r = _input_compat('> {0} (y/N) '.format(question))
            else:
                r = _input_compat('> {0} (y/n) '.format(question))

            r = r.strip().lower()

            if r in ('y', 'yes'):
                r = True
                break
            elif r in ('n', 'no'):
                r = False
                break
            elif not r:
                r = default
                break
            else:
                print("You must answer 'yes' or 'no'")
        return r
    elif answer == int:
        r = None
        while True:
            if default:
                r = _input_compat('> {0} [{1}] '.format(question, default))
            else:
                r = _input_compat('> {0} '.format(question))

            r = r.strip()

            if not r:
                r = default
                break

            try:
                r = int(r)
                break
            except:
                print('You must enter an integer')
        return r
    elif answer == list:
        # For checking multiple options
        r = None
        while True:
            if default:
                r = _input_compat('> {0} [{1}] '.format(question, default))
            else:
                r = _input_compat('> {0} '.format(question))

            r = r.strip()

            if not r:
                r = default
                break

            # try:
            if int(r) in range(1, len(options)+1):
                break
            else:
                print('Please select valid option: ' + '/'.join('{}'.format(s) for _, s in enumerate(options)))
            # except:
            #     print('Not a valid option')
        return r
    if answer == dateObject:
        r = ''
        while True:
            if default:
                r = _input_compat('> {0} [{1}] '.format(question, default))
            else:
                r = _input_compat('> {0} '.format(question, default))

            r = r.strip()

            if not r:
                r = default
                break

            try:
                datetime.datetime.strptime(r, '%Y-%m-%d')
                break
            except ValueError:
                print("Incorrect data format, should be YYYY-MM-DD")

        return r

    else:
        raise NotImplemented(
            'Argument `answer` must be str_compat, bool, or integer')


def ask_timezone(question, default, tzurl):
    """Prompt for time zone and validate input"""
    lower_tz = [tz.lower() for tz in pytz.all_timezones]
    while True:
        r = ask(question, str_compat, default)
        r = r.strip().replace(' ', '_').lower()
        if r in lower_tz:
            r = pytz.all_timezones[lower_tz.index(r)]
            break
        else:
            print('Please enter a valid time zone:\n'
                  ' (check [{0}])'.format(tzurl))
    return r

def config_reader(filename, exists=False):
    config = ConfigParser.RawConfigParser()
    if exists:
        config.read(filename)
        CONF['consumer_key'] = config.get('Credentials', 'consumer_key')
        CONF['consumer_secret'] = config.get('Credentials', 'consumer_secret')
        CONF['api_key'] = config.get('Credentials', 'api_key')
        CONF['api_secret'] = config.get('Credentials', 'api_secret')
    else:
        config.add_section('Credentials')
        config.set('Credentials', 'api_secret', CONF['api_secret'])
        config.set('Credentials', 'api_key', CONF['api_key'])
        config.set('Credentials', 'consumer_secret', CONF['consumer_secret'])
        config.set('Credentials', 'consumer_key', CONF['consumer_key'])

        # Writing our configuration file to 'example.cfg'
        with open(filename, 'wb') as configfile:
            config.write(configfile)


def oauth_req(url, http_method="GET", post_body="", http_headers=None):
    consumer_key = CONF['consumer_key']
    consumer_secret = CONF['consumer_secret']
    key = CONF['api_key']
    secret = CONF['api_secret']
    consumer = oauth2.Consumer(key=consumer_key, secret=consumer_secret)
    token = oauth2.Token(key=key, secret=secret)
    client = oauth2.Client(consumer, token)
    resp, content = client.request(url, method=http_method, body=post_body, headers=http_headers)
    return content


def follow_user(tweet_data, like):
    following_users = []
    try:
        for tweet in tweet_data:
            user_info = tweet['user']
            request_sent = user_info['follow_request_sent']
            following = user_info['following']
            if not (request_sent or following):
                if like:
                    like_params = urllib.urlencode({'id': tweet['id']})
                    like_tweet = oauth_req(settings.TWITTER_API_URL + '/favorites/create.json?' + like_params,
                                       http_method="POST")
                    print('Liked tweet. Sleeping 10s before follow.')
                    time.sleep(10)
                user_id = user_info['id']
                parameter_encode = urllib.urlencode({'user_id': user_id})
                # TODO Add fake user-agent
                follow_request = oauth_req(settings.TWITTER_API_URL + '/friendships/create.json?' + parameter_encode,
                                           http_method="POST")
                follow_response = json.loads(follow_request)
                if 'following' in follow_response:
                    with open('user.csv', 'a') as csv_file:
                        writer = csv.writer(csv_file, delimiter=str('\t'))
                        writer.writerow([
                            user_id,
                            unicode(user_info['screen_name']).encode("utf-8"),
                            unicode(user_info['name']).encode("utf-8"),
                            unicode(user_info['description']).encode("utf-8"),
                            unicode(user_info['location']).encode("utf-8"),
                            user_info['followers_count']
                                         ])
                    following_users.append({
                        'user_id': user_id,
                        'screen_name': user_info['screen_name'],
                        'name': user_info['name'],
                        'description': user_info['description'],
                        'location': user_info['location'],
                        'followers_count': user_info['followers_count']
                    })
                    print('Following: %s.\n' % user_info['screen_name'])
                    print('Sleeping 10secs since next follow request.\n')
                    time.sleep(10)
    except Exception as e:
        print(e)
    return following_users


def get_json_data(url, parameters, like=False):
    json_element = {"users": []}
    page = 1
    max_id = None
    while True:
        parameter_encode = urllib.urlencode(parameters)
        try:
            search_result = oauth_req(url + parameter_encode)
        except socket.error:
            print('Connection timed-out. Try again later.')
            break
        search_result = json.loads(search_result)
        try:
            statuses = search_result['statuses']
            assert len(statuses) > 1
        except (KeyError, AssertionError):
            if not max_id:
                print('Empty response received.')
            break
        followed_user = follow_user(statuses, like)
        json_element['users'].extend(followed_user)
        max_id = statuses[-1]['id']
        parameters['max_id'] = max_id

    return json_element


def main():

    parser = argparse.ArgumentParser(
        description="CLI tool to fetch twitter data",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    print(r'''Welcome to Follow Tweet v{v}.

$$$$$$$$\        $$\ $$\                               $$$$$$$$\                                 $$\
$$  _____|       $$ |$$ |                              \__$$  __|                                $$ |
$$ |    $$$$$$\  $$ |$$ | $$$$$$\  $$\  $$\  $$\          $$ |$$\  $$\  $$\  $$$$$$\   $$$$$$\ $$$$$$\
$$$$$\ $$  __$$\ $$ |$$ |$$  __$$\ $$ | $$ | $$ |         $$ |$$ | $$ | $$ |$$  __$$\ $$  __$$\\_$$  _|
$$  __|$$ /  $$ |$$ |$$ |$$ /  $$ |$$ | $$ | $$ |         $$ |$$ | $$ | $$ |$$$$$$$$ |$$$$$$$$ | $$ |
$$ |   $$ |  $$ |$$ |$$ |$$ |  $$ |$$ | $$ | $$ |         $$ |$$ | $$ | $$ |$$   ____|$$   ____| $$ |$$\
$$ |   \$$$$$$  |$$ |$$ |\$$$$$$  |\$$$$$\$$$$  |         $$ |\$$$$$\$$$$  |\$$$$$$$\ \$$$$$$$\  \$$$$  |
\__|    \______/ \__|\__| \______/  \_____\____/          \__| \_____\____/  \_______| \_______|  \____/



This script will help you like user tweets and follow them.

Please answer the following questions so this script can generate your
required output.

    '''.format(v=__version__))
    configfile = 'twitter.cfg'
    if os.path.isfile(configfile):
        config_reader(configfile, exists=True)
    CONF['consumer_key'] = ask('Your Application\'s Consumer Key(API Key)? Found here: https://apps.twitter.com/',
                               answer=str_compat, default=CONF['consumer_key'])
    CONF['consumer_secret'] = ask('Your Application\'s Consumer Secret(API Secret)? ' +
                                  'Found here: https://apps.twitter.com/app/{ Your API}/keys',
                                  answer=str_compat, default=CONF['consumer_secret'])
    CONF['api_key'] = ask('Your Access Token? ' +
                          'Found here: https://apps.twitter.com/app/{ Your API}/keys',
                          answer=str_compat, default=CONF['api_key'])
    CONF['api_secret'] = ask('Your Access Token Secret? ' +
                             'Found here: https://apps.twitter.com/app/{ Your API}/keys',
                             answer=str_compat, default=CONF['api_secret'])
    if not os.path.isfile(configfile):
        config_reader(configfile)

    action_type = ask('Follow or Un-follow? 1/Follow 2/Unfollow',
                           answer=list, default='1', options=[1, 2])
    if action_type == '1':
        like_value = ask('Like tweet? Y/N',
                   answer=str_compat, default='N')
        like = True if like_value == 'Y' else False
        request_params = {}

        print("A list of questions would now be asked to fetch Tweets. And those users will be followed.")
        CONF['query'] = ask('Search terms? ' +
                            'Found here: https://dev.twitter.com/rest/public/search',
                            answer=str_compat)
        request_params['q'] = CONF['query']
        result_data_type = ask('Type of search results? 1/Popular 2/Recent 3/Mixed',
                               answer=list, default='1', options=[1, 2, 3])
        request_params['result_type'] = RESULT_MAP[result_data_type]
        location = ask('Location? Eg. 1600 Amphitheatre Parkway, Mountain View, CA',
                       answer=str_compat, default=" ")
        if location.strip():
            encode_location = urllib.urlencode({'address': location})
            response_location = requests.get('https://maps.googleapis.com/maps/api/geocode/json?' +
                                             encode_location)
            try:
                location_json = response_location.json()
                location_data = location_json['results'][0]['geometry']['location']
                location_array = [str(value) for value in location_data.itervalues()]
                if location_array:
                    radius_mi = ask('Distance to search within in miles',
                                    answer=str_compat)

                    location_array.append(radius_mi + u'mi')
                    CONF['geocode'] = ",".join(location_array)
                    request_params['geocode'] = CONF['geocode']
            except:
                print('Unable to fetch lat and long for location')
        url = settings.TWITTER_API_URL + '/search/tweets.json?'
        print('Sending request to API...')
        json_search_data = get_json_data(url, request_params, like)
        if json_search_data['users']:
            print('Output file generated.')
            print('Process complete. Total users followed %d' % len(json_search_data['users']))
        else:
            print('Search yield no results')
    else:
        print('Un-following Users.')
        #follow_check()

if __name__ == "__main__":
    main()

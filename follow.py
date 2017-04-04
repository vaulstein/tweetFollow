#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import csv
import json
import socket
import time
import urllib

import requests

import common
import unfollow


def get_unfollow_user():
    unfollow_id = []
    with open('unfollow.csv', 'r') as csv_file:
        reader = csv.reader(csv_file, delimiter=str('\t'))
        for row in reader:
            unfollow_id.append(int(row[0]))
    return unfollow_id


def follow_user(tweet_data, like):
    following_users = []
    unfollowed_users = get_unfollow_user()
    try:
        for tweet in tweet_data:
            if common.CONF['type_of_follow'] == '1':
                user_info = tweet['user']
                user_id = user_info['id']
                request_sent = user_info['follow_request_sent']
                following = user_info['following']
                tweet_id = tweet['id']
                tweet_text = tweet['text']
            else:
                user_info = tweet
                user_id = user_info['id']
                request_sent = user_info['follow_request_sent']
                following = user_info['following']
                try:
                    tweet_id = tweet['status']['id']
                    tweet_text = tweet['status']['text']
                except KeyError:
                    tweet_id = None
                    tweet_text = None
                    print("User hasn't tweeted yet.")
            if (user_id not in unfollowed_users) and not (request_sent or following):
                if like:
                    like_params = urllib.urlencode({'id': tweet_id})
                    like_tweet = common.oauth_req(common.TWITTER_API_URL + '/favorites/create.json?' + like_params,
                                                  http_method="POST")
                    print('Liked tweet. Sleeping 10s before follow.')
                    time.sleep(30)
                parameter_encode = urllib.urlencode({'user_id': user_id})
                # TODO Add fake user-agent
                follow_request = common.oauth_req(
                    common.TWITTER_API_URL + '/friendships/create.json?' + parameter_encode,
                    http_method="POST")
                try:
                    follow_response = json.loads(follow_request)
                    if 'errors' in follow_response:
                        print('You have reached your limit of following 1000 users per day.')
                        print('The next set of users will be followed tomorrow.')
                        time.sleep(86400)
                    if 'following' in follow_response:
                        with open('user.csv', 'a') as csv_file:
                            writer = csv.writer(csv_file, delimiter=str('\t'))
                            writer.writerow([
                                user_id,
                                unicode(user_info['screen_name']).encode("utf-8"),
                                unicode(user_info['name']).encode("utf-8"),
                                unicode(user_info['description']).encode("utf-8"),
                                unicode(user_info['location']).encode("utf-8"),
                                unicode(tweet_id).encode("utf-8"),
                                unicode(tweet_text).encode("utf-8"),
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
                        time.sleep(30)
                except Exception as e:
                    print(e)
                    continue
    except Exception as e:
        print(e)
    return following_users


def get_json_data(url, parameters, like=False, favourite=False):
    json_element = {"users": []}
    cursor = -1
    max_id = None
    while True:
        parameter_encode = urllib.urlencode(parameters)
        try:
            search_result = common.oauth_req(url + parameter_encode)
        except socket.error:
            print('Connection timed-out. Try again later.')
            break
        search_result = json.loads(search_result)
        if common.CONF['type_of_follow'] == '1':
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
        else:
            try:
                followers = search_result['users']
                assert len(followers) > 1
            except (KeyError, AssertionError):
                if cursor != -1:
                    print('Empty response received.')
                break
            followed_user = follow_user(followers, like)
            json_element['users'].extend(followed_user)
            cursor = search_result['next_cursor']
            parameters['cursor'] = cursor

    return json_element


def main():
    common.start()
    action_type = common.ask('Follow or Un-follow? 1/Follow 2/Unfollow',
                             answer=list, default='1', options=[1, 2])
    if action_type == '1':
        like = common.ask('Like tweet? ',
                          answer=bool, default='N')
        request_params = {}
        common.CONF['type_of_follow'] = common.ask(
            'Would you like to follow people based on tweets or follow followers of a user?' +
            " 1/By Tweet 2/Follow User's Followers", answer=list,
            default='1', options=[1, 2]
            )
        if common.CONF['type_of_follow'] == '1':
            print("A list of questions would now be asked to fetch Tweets. And those users will be followed.")
            common.CONF['query'] = common.ask('Search terms? ' +
                                          'Found here: https://dev.twitter.com/rest/public/search',
                                          answer=common.str_compat)
            request_params['q'] = common.CONF['query']
            result_data_type = common.ask('Type of search results? 1/Popular 2/Recent 3/Mixed',
                                      answer=list, default='1', options=[1, 2, 3])
            request_params['result_type'] = common.RESULT_MAP[result_data_type]
            location = common.ask('Location? Eg. 1600 Amphitheatre Parkway, Mountain View, CA',
                              answer=common.str_compat, default=" ")
            if location.strip():
                encode_location = urllib.urlencode({'address': location})
                response_location = requests.get('https://maps.googleapis.com/maps/api/geocode/json?' +
                                             encode_location)
                try:
                    location_json = response_location.json()
                    location_data = location_json['results'][0]['geometry']['location']
                    location_array = [str(value) for value in location_data.itervalues()]
                    if location_array:
                        radius_mi = common.ask('Distance to search within in miles',
                                               answer=common.str_compat)

                        location_array.append(radius_mi + u'mi')
                        common.CONF['geocode'] = ",".join(location_array)
                        request_params['geocode'] = common.CONF['geocode']
                except:
                    print('Unable to fetch lat and long for location')
            url = common.TWITTER_API_URL + '/search/tweets.json?'
            print('Sending request to API...')
        else:
            user_followers = common.ask("Enter the username of the user who's followers you want to follow?",
                                        answer=common.str_compat)
            url = common.TWITTER_API_URL + '/followers/list.json?'
            request_params['screen_name'] = user_followers
        json_search_data = get_json_data(url, request_params, like)
        if json_search_data['users']:
            print('Output file generated.')
            print('Process complete. Total users followed %d' % len(json_search_data['users']))
        else:
            print('Search yield no results')
    else:
        print('Un-following Users and sending Thank you message to following users.')
        custom_message = common.ask('Custom message for new followers? Or Add message to ThankYouMessage.txt',
                                    answer=common.str_compat, default=" ")
        unfollow.follow_check(custom_message)

if __name__ == "__main__":
    main()

import csv
import json
import socket
import sys
import time
import urllib

import common


def return_user():
    try:
        lines = open('last_read_row.txt', 'rb')
        for line in lines:
            last_row = int(line)
    except IOError:
        last_row = 0
    with open('user.csv', 'rb') as user_file:
        reader = csv.reader(user_file, delimiter="\t")
        rows = [r for r in reader]


    user_list = rows[last_row:]
    return {'user_list': user_list, 'last_row': last_row}


def get_followers():
    cursor = -1
    while True:
        parameters = {'skip_status': True, 'include_user_entities': False, 'cursor': cursor}
        parameter_encode = urllib.urlencode(parameters)
        try:
            get_user_list = common.oauth_req(common.TWITTER_API_URL + '/friends/list.json?' + parameter_encode)
        except socket.error:
            print('Connection timed-out. Try again later.')
            break
        try:
            following_data = json.loads(get_user_list)
            if 'users' in following_data:
                user_list = following_data['users']
                for each_user in user_list:
                    follower_count = each_user["followers_count"]
                    following = is_following(each_user['id'])
                    if follower_count < 200 and not following:
                        print(
                        'Un-following user %s with follower count %d' % (each_user['screen_name'], follower_count))
                        un_follow_request(each_user['id'])
                cursor = following_data['next_cursor']
                parameters['cursor'] = cursor
                time.sleep(5)
        except KeyError:
            print(following_data['errors'][0]['message'])
        except ValueError:
            break
            print('Rate limit exceeded.')



def send_message(user_id, message=None):
    if not message.strip():
        message_data = open('ThankYouMessage.txt', 'rb')
        message = message_data.read()
    parameter_encode = urllib.urlencode({'user_id': user_id, 'text': message})
    message_call = common.oauth_req(common.TWITTER_API_URL + '/direct_messages/new.json?' + parameter_encode,
                                    http_method="POST")
    try:
        message_call_data = json.loads(message_call)
        if 'created_at' in message_call_data:
            print('Thank you message sent.')
            time.sleep(10)
    except ValueError:
        print('Message could not be sent')


def is_following(user_id):
    parameter_encode = urllib.urlencode({'target_id': user_id})
    try:
        follow_status_call = common.oauth_req(common.TWITTER_API_URL + '/friendships/show.json?' + parameter_encode)
        try:
            follow_status_data = json.loads(follow_status_call)
            follow_status = follow_status_data['relationship']['target']['following']
        except KeyError:
            print(follow_status_data['errors'][0]['message'])
            follow_status = None
        except ValueError:
            print('Rate limit exceeded.')
            sys.exit(0)
    except socket.error, v:
        print(v)
    time.sleep(10)
    return follow_status


def un_follow_request(user_id):
    parameter_encode = urllib.urlencode({'user_id': user_id})
    try:
        data = common.oauth_req(common.TWITTER_API_URL + '/friendships/destroy.json?' + parameter_encode,
                                http_method='POST')
        status = json.loads(data)
    except socket.error:
        status = None
        print('Connection Time-out.')
    if status and 'errors' in status:
        if status['errors'][0]['code'] == 34:
            print("User no longer exists.")
        else:
            print(status['errors'][0]['message'])
            sys.exit(0)
    time.sleep(10)
    return False


def un_follow(user_id, message):
    follow_status = is_following(user_id)
    if not follow_status:
        # Not following, un-follow
        if follow_status is None:
            return False
        else:
            return un_follow_request(user_id)
    else:
        send_message(user_id, message)
        return True


def follow_check(message=None):
    user_dict = return_user()
    user_data = user_dict['user_list']
    last_row = user_dict['last_row']
    count = 0
    for user in user_data:
        status = un_follow(user[0], message)
        if status:
            print('User with id %s followed you.' % user[0])
            with open('follow.csv', 'a') as csv_file:
                writer = csv.writer(csv_file, delimiter=str('\t'))
                writer.writerow(user)
        else:
            print('User with id %s did NOT follow you :( .' % user[0])
            with open('unfollow.csv', 'a') as csv_file:
                writer = csv.writer(csv_file, delimiter=str('\t'))
                writer.writerow(user)
        last_read = open('last_read_row.txt', 'wb')
        count += 1
        last_read.write(str(last_row + count))
        last_read.close()
    print('Process complete!')


def main():
    common.start()
    try:
        start_unfollow = common.ask('Unfollow from beginning of time? ', answer=bool, default='N')
        if start_unfollow:
            get_followers()
        else:
            custom_message = common.ask('Custom message for new followers?',
                                    answer=common.str_compat, default=" ")
            follow_check(custom_message.strip())
    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()
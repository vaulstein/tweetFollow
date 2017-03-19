import csv
import json
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
    last_read_file = open('last_read_row.txt', 'a')
    last_read_file.write(str(len(rows)))
    return user_list


def is_following(user_id):
    parameter_encode = urllib.urlencode({'target_id': user_id})
    follow_status_call = common.oauth_req(common.TWITTER_API_URL + '/friendships/show.json?' + parameter_encode)
    follow_status_data = json.loads(follow_status_call)
    follow_status = follow_status_data['relationship']['target']['following']
    time.sleep(5)
    return follow_status


def un_follow(user_id):
    follow_status = is_following(user_id)
    if not follow_status:
        # Not following, un-follow
        parameter_encode = urllib.urlencode({'user_id': user_id})
        common.oauth_req(common.TWITTER_API_URL + '/friendships/destroy.json?' + parameter_encode)
        time.sleep(5)
        return False
    else:
        return True


def follow_check():
    user_data = return_user()
    for user in user_data:
        status = un_follow(user[0])
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
    print('Process complete!')


def main():
    common.start()
    follow_check()


if __name__ == '__main__':
    main()
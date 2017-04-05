# [![Screenshot from 2017-03-16 22-02-35.png](https://s28.postimg.org/xzqkds41p/Screenshot_from_2017_03_16_22_02_35.png)](https://postimg.org/image/96h0d4l15/)


CLI interface to search users by tweets(hashtags, keywords, location) and follow those users.
Followers of a particular user can also be followed.
You can now Un-follow users who don't follow you and send a Thank You message to those who follow.

_Note: Do not edit the files created by the code. You can create a copy of those files and edit the copy._

## Follow Limit

Twitter has a limit of following 1000 users per day.
Once you receive this limit, you won't be allowed to follow more users for the day.

**The script has been automated to pause and resume the next day if you have reached your limit for the day.**

Trying to follow more user may result in your account being locked.
https://support.twitter.com/articles/66885


## Getting Started

These instructions will get you a copy of the project up and running on your local machine.

## Installation

    git clone https://github.com/vaulstein/tweetFollow.git
    cd tweetFollow
    pip install -r requirements.txt

## Usage

[![app.twitter.com.png](https://s4.postimg.org/5cwwhsgi5/app_twitter_com.png)](https://postimg.org/image/dv6cm4n0p/)

Create an app on twitter on the following link:
    [App on twitter](https://apps.twitter.com/)

After creating your app, you will find the App keys on the link: https://apps.twitter.com/app/{ API KEY }/keys

Run the following command:

    python follow.py

On running the script you would be asked a set of questions that would help in fetching the required data

     > Your Application's Consumer Key(API Key)? Found here: https://apps.twitter.com/
     > Your Application's Consumer Secret(API Secret)? Found here: https://apps.twitter.com/app/{ Your API}/keys
     > Your Access Token? Found here: https://apps.twitter.com/app/{ Your API}/keys
     > Your Access Token Secret? Found here: https://apps.twitter.com/app/{ Your API}/keys

You can either **follow** new users or **unfollow** users who haven't followed you back.

Select **1** to Follow Users, **2** to unfollow users.

If you decide to follow users, you can either search users by tweet and follow 
                        OR
provide the **screen_name** of a twitter user and follow his/her followers.

Please note, If you use the second option, it is advisable to also like/favourite that user's current tweet
 to avoid you account from being locked and also likes tend to get more followers.

If you use the search by tweet and follow option, you would be asked for the search parameters.

The different search parameters can be found here:
[Query parameters](https://dev.twitter.com/rest/public/search)

The first question is the query parameter, where you can use different operators to search data

For fetching Tweet search data, the below is an example of questions:

[![Screenshot from 2017-03-16 21-50-58.png](https://s22.postimg.org/8pv8przoh/Screenshot_from_2017_03_16_21_50_58.png)](https://postimg.org/image/iaevcnp0d/)


Remember twitter API is rate limited.
Rate limits for tweet search are 450/15 minutes.
Rate limits for user search are 900/15 minutes.

## Sending Messages 

To send Thank you messages to your followers you will need to select **Read, Write and Access direct messages** 
permissions.
This permission can be found here: 

[App on twitter](https://apps.twitter.com/)

[![message.png](https://s27.postimg.org/nv274c4ar/message.png)](https://postimg.org/image/6ujavnr9b/)

Add your default message to **ThankYouMessage.txt** or you can pass it at runtime also.

## Contributing

Please read [CONTRIBUTE.md](CONTRIBUTE.md) for details on our code of conduct, and the process for submitting pull requests to us.


## Authors

* **VAULSTEIN RODRIGUES** - *Initial work* - [Blog](https://vaulstein.github.io)



## Acknowledgments

* Code from [Pelican](https://github.com/getpelican/pelican) used
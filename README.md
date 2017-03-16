# FOLLOW TWEET


[![Screenshot from 2017-03-16 22-02-35.png](https://s28.postimg.org/xzqkds41p/Screenshot_from_2017_03_16_22_02_35.png)](https://postimg.org/image/96h0d4l15/)


CLI interface to fetch tweets based on keywords, hashtags and follow those users

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

Based on your selection you would be asked a few questions for the search parameters.

The different search parameters can be found here:
[Query parameters](https://dev.twitter.com/rest/public/search)

The first question is the query parameter, where you can use different operators to search data

For fetching Tweet search data, the below is an example of questions:

[![Screenshot from 2017-03-16 21-50-58.png](https://s22.postimg.org/8pv8przoh/Screenshot_from_2017_03_16_21_50_58.png)](https://postimg.org/image/iaevcnp0d/)

The last question would be the name of the output file you would want to write to.
If you specify the same file name as the last, remember to take a backup.

Remember twitter API is rate limited.
Rate limits for tweet search are 450/15 minutes.
Rate limits for user search are 900/15 minutes.


## Contributing

Please read [CONTRIBUTE.md](CONTRIBUTE.md) for details on our code of conduct, and the process for submitting pull requests to us.


## Authors

* **VAULSTEIN RODRIGUES** - *Initial work* - [Blog](https://vaulstein.github.io)



## Acknowledgments

* Code from [Pelican](https://github.com/getpelican/pelican) used
from itertools import count
import time
import requests


def get_all_tweets():
    return requests.get(
        'http://127.0.0.1:8005/api/tweets/').json()


def get_all_users():
    return requests.get(
        'http://127.0.0.1:8005/api/users/').json()


def add_tweet(tweet):
    return requests.put(
        f'http://127.0.0.1:8005/api/tweets/', json=tweet).json()


def find_tweets_by_id(id: str):
    return requests.get(
        f'http://127.0.0.1:8005/api/tweets/find_by_id?id={id}').json()


def delete_tweet(id: str):
    return requests.delete(
        f'http://127.0.0.1:8005/api/tweets/{id}').content


def filter_by_tweet(tweet: str):
    return requests.get(
        f'http://127.0.0.1:8005/api/tweets/filter_by_tweet/?tweet={tweet}').json()


def scroll_tweets(scroll_id: str):
    return requests.get(
        f'http://127.0.0.1:8005/api/tweets/scroll_by_scroll_id?scroll_id={scroll_id}').json()


def filter_by_dates(first_date: int, second_date: int):
    return requests.get(
        f'http://127.0.0.1:8005/api/tweets/filter_by_dates?first_date={first_date}&second_date={second_date}').json()


def tweets_api_test():
    print(len(get_all_tweets()))
    tweet = {
        "user_login": "krakazabra",
        "created_at": 1234567890,
        "tweet": "Updated tweet content",
        "likes": 10,
        "continent": "Europe"
    }
    added_id = add_tweet(tweet=tweet)
    print(added_id)
    print(find_tweets_by_id(added_id))
    filtered_by_tweets_values = filter_by_tweet(tweet="Trump")
    print(filtered_by_tweets_values)
    print(scroll_tweets(filtered_by_tweets_values["scroll_id"]))
    filtered_by_dates_values = filter_by_dates(
        first_date=20201015004631, second_date=20221015004631)
    print(filtered_by_dates_values)
    print(scroll_tweets(filtered_by_dates_values["scroll_id"]))
    print(delete_tweet(added_id))
    print(len(get_all_tweets()))


def find_user_by_id(id: str):
    return requests.get(
        f'http://127.0.0.1:8005/api/users/find_by_id?id={id}').json()


def users_api_test():
    user_id = get_all_users()[0]['id']
    print(find_user_by_id(id=user_id))


tweets_api_test()
# users_api_test()

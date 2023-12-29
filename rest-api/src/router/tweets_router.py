from typing import Any, Mapping, Sequence
from bson import ObjectId
from fastapi import APIRouter, Depends, status, Response
from repositories.mongo.tweets_collection import MongoTweetsCollection, MongoDBCollection
from repositories.elastic_search.tweets_collection import ElasticTweetsCollection, ElasticSearch
from pymemcache import HashClient
from utils.memcached_utils import MemcachedManager
from models.tweet import Tweet, TweetUpdate

router = APIRouter()


@router.get("/")
async def get_all_tweets(repository: MongoDBCollection = Depends(MongoTweetsCollection.get_instance)):
    result: Sequence[Tweet] = [Tweet.model_validate(user) for user in await repository.get_all(Tweet)]
    return result


@router.get("/filter_by_tweet")
async def filter_by_tweet(tweet: str, search_repository: ElasticSearch = Depends(ElasticTweetsCollection.get_instance)) -> Any:
    return await search_repository.find_by_atr("tweet", tweet)


@router.get("/filter_by_dates")
async def filter_by_dates(first_date: int, second_date: int, search_repository: ElasticSearch = Depends(ElasticTweetsCollection.get_instance)) -> Any:
    return await search_repository.find_by_dates(first_date, second_date)


@router.get("/scroll_by_scroll_id")
async def scroll_by_id(scroll_id: str, search_repository: ElasticSearch = Depends(ElasticTweetsCollection.get_instance)) -> Any:
    return await search_repository.scroll(scroll_id=scroll_id)


@router.get("/find_by_id", response_model=Tweet)
async def get_by_id(id: str,
                    repository: MongoTweetsCollection = Depends(
                        MongoTweetsCollection.get_instance)) -> Any:
    if not ObjectId.is_valid(id):
        return Response(status_code=status.HTTP_400_BAD_REQUEST)
    obj = await repository.get_by_id(Tweet, id)
    if obj is None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    return obj


@router.put("/")
async def add_tweet(tweet: TweetUpdate,
                    repository: MongoDBCollection = Depends(
                        MongoTweetsCollection.get_instance),
                    search_repository: ElasticSearch = Depends(ElasticTweetsCollection.get_instance)) -> str:
    tweet_id = await repository.create(tweet)
    await search_repository.create(tweet_id, TweetUpdate.model_dump(tweet))
    return tweet_id


@router.delete("/{tweet_id}")
async def delete_tweet(tweet_id: str,
                       repository: MongoDBCollection = Depends(
                           MongoTweetsCollection.get_instance),
                       search_repository: ElasticSearch = Depends(ElasticTweetsCollection.get_instance)) -> Response:
    if not ObjectId.is_valid(tweet_id):
        return Response(status_code=status.HTTP_400_BAD_REQUEST)
    obj = await repository.delete(tweet_id, Tweet)
    if obj is None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    await search_repository.delete(tweet_id)
    return Response(status_code=200, content=f"{tweet_id} was succesfully removed")


@router.put("/{tweet_id}", response_model=Tweet)
async def update_tweet(tweet_id: str,
                       obj_update_model: TweetUpdate,
                       repository: MongoDBCollection = Depends(
                           MongoTweetsCollection.get_instance),
                       search_repository: ElasticSearch = Depends(ElasticTweetsCollection.get_instance)) -> Any:
    if not ObjectId.is_valid(tweet_id):
        return Response(status_code=status.HTTP_400_BAD_REQUEST)
    obj = await repository.update(obj_update_model, Tweet, tweet_id)
    if obj is None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    await search_repository.update(tweet_id, obj_update_model)
    return obj

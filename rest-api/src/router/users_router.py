from typing import Any, Mapping, Sequence
from bson import ObjectId
from fastapi import APIRouter, Depends, status, Response
from repositories.mongo.users_collection import MongoUsersCollection, MongoDBCollection
from repositories.elastic_search.users_collection import ElasticUsersCollection, ElasticSearch
from pymemcache import HashClient
from utils.memcached_utils import MemcachedManager
from models.users import User, UserUpdate

router = APIRouter()


@router.get("/")
async def get_all_users(repository: MongoDBCollection = Depends(MongoUsersCollection.get_instance)):
    result: Sequence[User] = [User.model_validate(user) for user in await repository.get_all(User)]
    return result


@router.get("/filter_by_description")
async def filter_by_description(user: str, search_repository: ElasticSearch = Depends(ElasticUsersCollection.get_instance)) -> Any:
    return await search_repository.find_by_atr("user_description", user)


@router.get("/scroll_by_scroll_id")
async def scroll_by_id(scroll_id: str, search_repository: ElasticSearch = Depends(ElasticUsersCollection.get_instance)) -> Any:
    return await search_repository.scroll(scroll_id=scroll_id)


@router.get("/find_by_id", response_model=User)
async def get_by_id(id: str,
                    repository: MongoDBCollection = Depends(
                        MongoUsersCollection.get_instance),
                    memcached: HashClient = Depends(MemcachedManager.get_memcached_client)) -> Any:
    if not ObjectId.is_valid(id):
        return Response(status_code=status.HTTP_400_BAD_REQUEST)
    user = memcached.get(id)
    if user:
        return user
    obj = await repository.get_by_id(User, id)
    if obj is None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    memcached.add(id, obj, expire=60*15)
    return obj


@router.put("/")
async def add_user(user: UserUpdate,
                   repository: MongoDBCollection = Depends(
                       MongoUsersCollection.get_instance),
                   search_repository: ElasticSearch = Depends(ElasticUsersCollection.get_instance)) -> str:
    user_id = await repository.create(user)
    await search_repository.create(user_id, UserUpdate.model_dump(user))
    return user_id


@router.delete("/{user_id}")
async def delete_user(user_id: str,
                      repository: MongoDBCollection = Depends(
                          MongoUsersCollection.get_instance),
                      search_repository: ElasticSearch = Depends(ElasticUsersCollection.get_instance)) -> Response:
    if not ObjectId.is_valid(user_id):
        return Response(status_code=status.HTTP_400_BAD_REQUEST)
    obj = await repository.delete(user_id, User)
    if obj is None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    await search_repository.delete(user_id)
    return Response(status_code=200, content=f"{user_id} was succesfully removed")


@router.put("/{user_id}", response_model=User)
async def update_user(user_id: str,
                      obj_update_model: UserUpdate,
                      repository: MongoDBCollection = Depends(
                          MongoUsersCollection.get_instance),
                      search_repository: ElasticSearch = Depends(
                          ElasticUsersCollection.get_instance),
                      memcached: HashClient = Depends(MemcachedManager.get_memcached_client)) -> Any:
    if not ObjectId.is_valid(user_id):
        return Response(status_code=status.HTTP_400_BAD_REQUEST)
    old_obj = await repository.get_by_id(User, user_id)
    memcached.add(user_id, old_obj, expire=60*5)
    obj = await repository.update(obj_update_model, User, user_id)
    if obj is None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    await search_repository.update(user_id, obj_update_model)
    memcached.replace(id, obj)
    return obj

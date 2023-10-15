from typing import Union, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response, Query as QueryParam
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from starlette.status import HTTP_204_NO_CONTENT

from business.players_schema import *
from business.players_model import PlayerModel

from core.depends import CommonDependencies, get_db, Protect, zeauth_url
from core.logger import log
from core.query import *

from business.players_model import PlayerModel


router = APIRouter()


# list players
@router.get('/', tags=['players'], status_code=200, response_model=ReadPlayers)
async def list(request: Request, token: str = Depends(Protect), db: Session = Depends(get_db), commons: CommonDependencies = Depends(CommonDependencies)):
    token.auth(['admin', 'manager', 'user'])
    try:
        r = PlayerModel.objects(db).all(offset=commons.offset, limit=commons.size)
        return {
            'data': r,
            'page_size': commons.size,
            'next_page': int(commons.page) + 1
        }
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, "could not fetch list of player")

list.__doc__ = f" List players".expandtabs()


# get player
@router.get('/player_id', tags=['players'], response_model=ReadPlayer)
async def get(request: Request, player_id: str, db: Session = Depends(get_db), token: str = Depends(Protect)):
    token.auth(['admin', 'manager', 'user'])
    try:
        result = PlayerModel.objects(db).get(id=player_id)
        if result:
            return result
        else:
            raise FileNotFoundError
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail={
                "field_name": "{player_id}",
                "message": f"<{player_id}> record not found in  players"
            })
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, "could not fetch record <{player_id}>")

get.__doc__ = f" Get a specific player by its id".expandtabs()


# query player
@router.post('/q', tags=['players'], status_code=200)
async def query(q: QuerySchema, db: Session = Depends(get_db), token: str = Depends(Protect)):
    token.auth(['admin', 'manager', 'user'])
    try:
        size = q.limit if q.limit else 20
        page = int(q.skip)/size if q.skip else 1
        jq = JSONQ(db, PlayerModel)
        log.debug(q)
        allowed_aggregates = []
        result = jq.query(q, allowed_aggregates)
        return {
            'data': result.get("data", []),
            'aggregates': result.get("aggregates", []),
            'count': result.get("count", []),
            'page_size': size,
            'next_page': int(page) + 1
        }
    except UnkownOperator as e:
        log.debug(e)
        raise HTTPException(400, str(e))
    except ColumnNotFound as e:
        log.debug(e)
        raise HTTPException(400, str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, "could not fetch list of sessions due to unknown error")


# create player
@router.post('/', tags=['players'], status_code=201, response_model=ReadPlayer)
async def create(request: Request, player: CreatePlayer, db: Session = Depends(get_db), token: str = Depends(Protect)):
    token.auth(['manager']) 
    try:
        new_data = player.dict()
        kwargs = {
            "model_data": new_data,
            "signal_data": {
                "jwt": token.credentials,
                "new_data": new_data,
                "old_data": {},
                "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
            }
        }
        new_player = PlayerModel.objects(db).create(**kwargs)
        return new_player
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.pgerror)
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, f"creation of new player failed")

create.__doc__ = f" Create a new player".expandtabs()


# create multiple players
@router.post('/add-players', tags=['players'], status_code=201, response_model=List[ReadPlayer])
async def create_multiple_players(request: Request, players: List[CreatePlayer], db: Session = Depends(get_db), token: str = Depends(Protect)):
    token.auth(['manager']) 
    new_items, errors_info = [], []
    try:
        for player_index, player in enumerate(players):
            try:
                new_data = player.dict()
                kwargs = {
                    "model_data": new_data,
                    "signal_data": {
                        "jwt": token.credentials,
                        "new_data": new_data,
                        "old_data": {},
                        "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
                    }
                }
                new_players = PlayerModel.objects(db).create(only_add=True, **kwargs)
                new_items.append(new_players)
            except HTTPException as e:
                errors_info.append({"index": player_index, "errors": e.detail})

        db.commit()
        return new_items
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.pgerror)
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, f"creation of new players failed")

create.__doc__ = f" Create multiple new players".expandtabs()


# upsert multiple players
@router.post('/upsert-multiple-players', tags=['players'], status_code=201, response_model=List[ReadPlayer])
async def upsert_multiple_players(request: Request, players: List[UpsertPlayer], db: Session = Depends(get_db), token: str = Depends(Protect)):
    token.auth(['manager'])
    new_items, errors_info = [], []
    try:
        for player_index, player in enumerate(players):
            try:
                new_data = player.dict()
                kwargs = {
                    "model_data": new_data,
                    "signal_data": {
                        "jwt": token.credentials,
                        "new_data": new_data,
                        "old_data": {},
                        "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
                    }
                }
                if new_data['id']:
                    old_data = PlayerModel.objects(db).get(id=new_data['id'])
                    kwargs['signal_data']['old_data'] = old_data.__dict__ if old_data else {}

                    PlayerModel.objects(db).update(obj_id=new_data['id'], **kwargs)
                    updated_deployments = PlayerModel.objects(db).get(id=new_data['id'])
                    new_items.append(updated_deployments)
                else:
                    new_players = PlayerModel.objects(db).create(only_add=True, **kwargs)
                    new_items.append(new_players)
            except HTTPException as e:
                errors_info.append({"index": player_index, "errors": e.detail})

        db.commit()
        return new_items
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.pgerror)
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, f"upsert multiple players failed")

upsert_multiple_players.__doc__ = f" upsert multiple players".expandtabs()


# update player
@router.put('/player_id', tags=['players'], status_code=201)
async def update(request: Request, player_id: Union[str, int], player: CreatePlayer, db: Session = Depends(get_db), token: str = Depends(Protect)):
    token.auth(['admin', 'manager'])
    try:
        old_data = PlayerModel.objects(db).get(id=player_id)
        new_data = player.dict(exclude_unset=True)
        kwargs = {
            "model_data": new_data,
            "signal_data": {
                "jwt": token.credentials,
                "new_data": new_data,
                "old_data": old_data.__dict__ if old_data else {},
                "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
            }
        }
        PlayerModel.objects(db).update(obj_id=player_id, **kwargs)
        result = PlayerModel.objects(db).get(id=player_id)
        return result
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.pgerror)
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, "failed updating session with id <{session_id}>")

update.__doc__ = f" Update a player by its id and payload".expandtabs()


# delete player
@router.delete('/player_id', tags=['players'], status_code=HTTP_204_NO_CONTENT, response_class=Response)
async def delete(request: Request, player_id: Union[str, int], db: Session = Depends(get_db), token: str = Depends(Protect)):
    token.auth(['manager'])
    try:
        kwargs = {
            "model_data": {},
            "signal_data": {
                "jwt": token.credentials,
                "new_data": {},
                "old_data": {},
                "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
            }
        }
        PlayerModel.objects(db).delete(obj_id=player_id, **kwargs)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail={
                "field_name": "{player_id}",
                "message": f"<{player_id}> record not found in  players"
            })
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, "failed updating session with id <{session_id}>")

delete.__doc__ = f" Delete a player by its id".expandtabs()


# delete multiple players
@router.delete('/delete-players', tags=['players'], status_code=HTTP_204_NO_CONTENT, response_class=Response)
async def delete_multiple_players(request: Request, players_id: List[str] = QueryParam(), db: Session = Depends(get_db), token: str = Depends(Protect)):
    token.auth(['manager'])
    kwargs = {
        "model_data": {},
        "signal_data": {
            "jwt": token.credentials,
            "new_data": {},
            "old_data": {},
            "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
        }
    }
    PlayerModel.objects(db).delete_multiple(obj_ids=players_id, **kwargs)

delete.__doc__ = f" Delete multiple players by list of ids".expandtabs()

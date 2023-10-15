from typing import Union, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response, Query as QueryParam
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from starlette.status import HTTP_204_NO_CONTENT

from business.teams_schema import *
from business.teams_model import TeamModel

from core.depends import CommonDependencies, get_db, Protect, zeauth_url
from core.logger import log
from core.query import *
from actions import create_player_for_team
from business.teams_model import TeamModel


router = APIRouter()


# list teams
@router.get('/', tags=['teams'], status_code=200, response_model=ReadTeams)
async def list(request: Request, token: str = Depends(Protect), db: Session = Depends(get_db), commons: CommonDependencies = Depends(CommonDependencies)):
    token.auth(['admin'])
    try:
        r = TeamModel.objects(db).all(offset=commons.offset, limit=commons.size)
        return {
            'data': r,
            'page_size': commons.size,
            'next_page': int(commons.page) + 1
        }
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, "could not fetch list of team")

list.__doc__ = f" List teams".expandtabs()


# get team
@router.get('/team_id', tags=['teams'], response_model=ReadTeam)
async def get(request: Request, team_id: str, db: Session = Depends(get_db), token: str = Depends(Protect)):
    token.auth(['admin', 'user'])
    try:
        result = TeamModel.objects(db).get(id=team_id)
        if result:
            return result
        else:
            raise FileNotFoundError
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail={
                "field_name": "{team_id}",
                "message": f"<{team_id}> record not found in  teams"
            })
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, "could not fetch record <{team_id}>")

get.__doc__ = f" Get a specific team by its id".expandtabs()


# query team
@router.post('/q', tags=['teams'], status_code=200)
async def query(q: QuerySchema, db: Session = Depends(get_db), token: str = Depends(Protect)):
    token.auth(['admin'])
    try:
        size = q.limit if q.limit else 20
        page = int(q.skip)/size if q.skip else 1
        jq = JSONQ(db, TeamModel)
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


# create team
@router.post('/', tags=['teams'], status_code=201, response_model=ReadTeam)
async def create(request: Request, team: CreateTeam, db: Session = Depends(get_db), token: str = Depends(Protect)):
    token.auth(['admin']) 
    try:
        new_data = team.dict()
        kwargs = {
            "model_data": new_data,
            "signal_data": {
                "jwt": token.credentials,
                "new_data": new_data,
                "old_data": {},
                "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
            }
        }
        new_team = TeamModel.objects(db).create(**kwargs)
        return new_team
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.pgerror)
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, f"creation of new team failed")

create.__doc__ = f" Create a new team".expandtabs()


# create multiple teams
@router.post('/add-teams', tags=['teams'], status_code=201, response_model=List[ReadTeam])
async def create_multiple_teams(request: Request, teams: List[CreateTeam], db: Session = Depends(get_db), token: str = Depends(Protect)):
    token.auth(['admin']) 
    new_items, errors_info = [], []
    try:
        for team_index, team in enumerate(teams):
            try:
                new_data = team.dict()
                kwargs = {
                    "model_data": new_data,
                    "signal_data": {
                        "jwt": token.credentials,
                        "new_data": new_data,
                        "old_data": {},
                        "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
                    }
                }
                new_teams = TeamModel.objects(db).create(only_add=True, **kwargs)
                new_items.append(new_teams)
            except HTTPException as e:
                errors_info.append({"index": team_index, "errors": e.detail})

        db.commit()
        return new_items
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.pgerror)
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, f"creation of new teams failed")

create.__doc__ = f" Create multiple new teams".expandtabs()


# upsert multiple teams
@router.post('/upsert-multiple-teams', tags=['teams'], status_code=201, response_model=List[ReadTeam])
async def upsert_multiple_teams(request: Request, teams: List[UpsertTeam], db: Session = Depends(get_db), token: str = Depends(Protect)):
    token.auth(['admin'])
    new_items, errors_info = [], []
    try:
        for team_index, team in enumerate(teams):
            try:
                new_data = team.dict()
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
                    old_data = TeamModel.objects(db).get(id=new_data['id'])
                    kwargs['signal_data']['old_data'] = old_data.__dict__ if old_data else {}

                    TeamModel.objects(db).update(obj_id=new_data['id'], **kwargs)
                    updated_deployments = TeamModel.objects(db).get(id=new_data['id'])
                    new_items.append(updated_deployments)
                else:
                    new_teams = TeamModel.objects(db).create(only_add=True, **kwargs)
                    new_items.append(new_teams)
            except HTTPException as e:
                errors_info.append({"index": team_index, "errors": e.detail})

        db.commit()
        return new_items
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.pgerror)
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, f"upsert multiple teams failed")

upsert_multiple_teams.__doc__ = f" upsert multiple teams".expandtabs()


# update team
@router.put('/team_id', tags=['teams'], status_code=201)
async def update(request: Request, team_id: Union[str, int], team: CreateTeam, db: Session = Depends(get_db), token: str = Depends(Protect)):
    token.auth(['admin'])
    try:
        old_data = TeamModel.objects(db).get(id=team_id)
        new_data = team.dict(exclude_unset=True)
        kwargs = {
            "model_data": new_data,
            "signal_data": {
                "jwt": token.credentials,
                "new_data": new_data,
                "old_data": old_data.__dict__ if old_data else {},
                "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
            }
        }
        TeamModel.objects(db).update(obj_id=team_id, **kwargs)
        result = TeamModel.objects(db).get(id=team_id)
        return result
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.pgerror)
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, "failed updating session with id <{session_id}>")

update.__doc__ = f" Update a team by its id and payload".expandtabs()


# delete team
@router.delete('/team_id', tags=['teams'], status_code=HTTP_204_NO_CONTENT, response_class=Response)
async def delete(request: Request, team_id: Union[str, int], db: Session = Depends(get_db), token: str = Depends(Protect)):
    token.auth(['admin'])
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
        TeamModel.objects(db).delete(obj_id=team_id, **kwargs)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail={
                "field_name": "{team_id}",
                "message": f"<{team_id}> record not found in  teams"
            })
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, "failed updating session with id <{session_id}>")

delete.__doc__ = f" Delete a team by its id".expandtabs()


# delete multiple teams
@router.delete('/delete-teams', tags=['teams'], status_code=HTTP_204_NO_CONTENT, response_class=Response)
async def delete_multiple_teams(request: Request, teams_id: List[str] = QueryParam(), db: Session = Depends(get_db), token: str = Depends(Protect)):
    token.auth(['admin'])
    kwargs = {
        "model_data": {},
        "signal_data": {
            "jwt": token.credentials,
            "new_data": {},
            "old_data": {},
            "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
        }
    }
    TeamModel.objects(db).delete_multiple(obj_ids=teams_id, **kwargs)

delete.__doc__ = f" Delete multiple teams by list of ids".expandtabs()

from typing import Union, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response, Query as QueryParam
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from starlette.status import HTTP_204_NO_CONTENT

from business.stadiums_schema import *
from business.stadiums_model import StadiumModel

from core.depends import CommonDependencies, get_db, Protect, zeauth_url
from core.logger import log
from core.query import *

from business.stadiums_model import StadiumModel


router = APIRouter()


# list stadiums
@router.get('/', tags=['stadiums'], status_code=200, response_model=ReadStadiums)
async def list(request: Request, token: str = Depends(Protect), db: Session = Depends(get_db), commons: CommonDependencies = Depends(CommonDependencies)):
    token.auth(['admin', 'manager', 'user'])
    try:
        r = StadiumModel.objects(db).all(offset=commons.offset, limit=commons.size)
        return {
            'data': r,
            'page_size': commons.size,
            'next_page': int(commons.page) + 1
        }
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, "could not fetch list of stadium")

list.__doc__ = f" List stadiums".expandtabs()


# get stadium
@router.get('/stadium_id', tags=['stadiums'], response_model=ReadStadium)
async def get(request: Request, stadium_id: str, db: Session = Depends(get_db), token: str = Depends(Protect)):
    token.auth(['admin', 'manager', 'user'])
    try:
        result = StadiumModel.objects(db).get(id=stadium_id)
        if result:
            return result
        else:
            raise FileNotFoundError
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail={
                "field_name": "{stadium_id}",
                "message": f"<{stadium_id}> record not found in  stadiums"
            })
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, "could not fetch record <{stadium_id}>")

get.__doc__ = f" Get a specific stadium by its id".expandtabs()


# query stadium
@router.post('/q', tags=['stadiums'], status_code=200)
async def query(q: QuerySchema, db: Session = Depends(get_db), token: str = Depends(Protect)):
    token.auth(['admin', 'manager', 'user'])
    try:
        size = q.limit if q.limit else 20
        page = int(q.skip)/size if q.skip else 1
        jq = JSONQ(db, StadiumModel)
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


# create stadium
@router.post('/', tags=['stadiums'], status_code=201, response_model=ReadStadium)
async def create(request: Request, stadium: CreateStadium, db: Session = Depends(get_db), token: str = Depends(Protect)):
    token.auth(['admin']) 
    try:
        StadiumModel.validate_unique_name_location(db, stadium.name, stadium.location)
        new_data = stadium.dict()
        kwargs = {
            "model_data": new_data,
            "signal_data": {
                "jwt": token.credentials,
                "new_data": new_data,
                "old_data": {},
                "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
            }
        }
        new_stadium = StadiumModel.objects(db).create(**kwargs)
        return new_stadium
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.pgerror)
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, f"creation of new stadium failed")

create.__doc__ = f" Create a new stadium".expandtabs()


# create multiple stadiums
@router.post('/add-stadiums', tags=['stadiums'], status_code=201, response_model=List[ReadStadium])
async def create_multiple_stadiums(request: Request, stadiums: List[CreateStadium], db: Session = Depends(get_db), token: str = Depends(Protect)):
    token.auth(['admin']) 
    new_items, errors_info = [], []
    try:
        for stadium_index, stadium in enumerate(stadiums):
            try:
                StadiumModel.validate_unique_name_location(db, stadium.name, stadium.location)
                new_data = stadium.dict()
                kwargs = {
                    "model_data": new_data,
                    "signal_data": {
                        "jwt": token.credentials,
                        "new_data": new_data,
                        "old_data": {},
                        "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
                    }
                }
                new_stadiums = StadiumModel.objects(db).create(only_add=True, **kwargs)
                new_items.append(new_stadiums)
            except HTTPException as e:
                errors_info.append({"index": stadium_index, "errors": e.detail})

        if errors_info:
            return JSONResponse(errors_info, 422)
        db.commit()
        return new_items
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.pgerror)
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, f"creation of new stadiums failed")

create.__doc__ = f" Create multiple new stadiums".expandtabs()


# upsert multiple stadiums
@router.post('/upsert-multiple-stadiums', tags=['stadiums'], status_code=201, response_model=List[ReadStadium])
async def upsert_multiple_stadiums(request: Request, stadiums: List[UpsertStadium], db: Session = Depends(get_db), token: str = Depends(Protect)):
    token.auth(['admin'])
    new_items, errors_info = [], []
    try:
        for stadium_index, stadium in enumerate(stadiums):
            try:
                StadiumModel.validate_unique_name_location(db, stadium.name, stadium.location)
                new_data = stadium.dict()
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
                    old_data = StadiumModel.objects(db).get(id=new_data['id'])
                    kwargs['signal_data']['old_data'] = old_data.__dict__ if old_data else {}

                    StadiumModel.objects(db).update(obj_id=new_data['id'], **kwargs)
                    updated_deployments = StadiumModel.objects(db).get(id=new_data['id'])
                    new_items.append(updated_deployments)
                else:
                    new_stadiums = StadiumModel.objects(db).create(only_add=True, **kwargs)
                    new_items.append(new_stadiums)
            except HTTPException as e:
                errors_info.append({"index": stadium_index, "errors": e.detail})

        if errors_info:
            return JSONResponse(errors_info, 422)
        db.commit()
        return new_items
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.pgerror)
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, f"upsert multiple stadiums failed")

upsert_multiple_stadiums.__doc__ = f" upsert multiple stadiums".expandtabs()


# update stadium
@router.put('/stadium_id', tags=['stadiums'], status_code=201)
async def update(request: Request, stadium_id: Union[str, int], stadium: CreateStadium, db: Session = Depends(get_db), token: str = Depends(Protect)):
    token.auth(['admin'])
    try:
        StadiumModel.validate_unique_name_location(db, stadium.name, stadium.location, stadium_id)
        old_data = StadiumModel.objects(db).get(id=stadium_id)
        new_data = stadium.dict(exclude_unset=True)
        kwargs = {
            "model_data": new_data,
            "signal_data": {
                "jwt": token.credentials,
                "new_data": new_data,
                "old_data": old_data.__dict__ if old_data else {},
                "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
            }
        }
        StadiumModel.objects(db).update(obj_id=stadium_id, **kwargs)
        result = StadiumModel.objects(db).get(id=stadium_id)
        return result
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.pgerror)
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, "failed updating session with id <{session_id}>")

update.__doc__ = f" Update a stadium by its id and payload".expandtabs()


# delete stadium
@router.delete('/stadium_id', tags=['stadiums'], status_code=HTTP_204_NO_CONTENT, response_class=Response)
async def delete(request: Request, stadium_id: Union[str, int], db: Session = Depends(get_db), token: str = Depends(Protect)):
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
        StadiumModel.objects(db).delete(obj_id=stadium_id, **kwargs)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail={
                "field_name": "{stadium_id}",
                "message": f"<{stadium_id}> record not found in  stadiums"
            })
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, "failed updating session with id <{session_id}>")

delete.__doc__ = f" Delete a stadium by its id".expandtabs()


# delete multiple stadiums
@router.delete('/delete-stadiums', tags=['stadiums'], status_code=HTTP_204_NO_CONTENT, response_class=Response)
async def delete_multiple_stadiums(request: Request, stadiums_id: List[str] = QueryParam(), db: Session = Depends(get_db), token: str = Depends(Protect)):
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
    StadiumModel.objects(db).delete_multiple(obj_ids=stadiums_id, **kwargs)

delete.__doc__ = f" Delete multiple stadiums by list of ids".expandtabs()

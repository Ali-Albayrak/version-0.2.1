from typing import Union, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response, Query as QueryParam
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from starlette.status import HTTP_204_NO_CONTENT, HTTP_200_OK, HTTP_201_CREATED

from business.apps_schema import *
from business.apps_model import AppModel

from core.depends import CommonDependencies, get_async_db, get_sync_db, Protect, zeauth_url
from core.logger import log
from core.query import *

from business.apps_model import AppModel


router = APIRouter()


  
# list apps
@router.get('/', tags=['apps'], status_code=HTTP_200_OK, summary="List apps", response_model=ReadApps)
async def list(request: Request, token: str = Depends(Protect), db: AsyncSession = Depends(get_async_db), commons: CommonDependencies = Depends(CommonDependencies)):
    token.auth(['zekoder-zestudio-apps-list', 'zekoder-zestudio-apps-get'])
    try:
        obj = await AppModel.objects(db)
        result = await obj.all(offset=commons.offset, limit=commons.size)
        return {
            'data': result,
            'page_size': commons.size,
            'next_page': int(commons.page) + 1
        }
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, "could not fetch list of app")

list.__doc__ = f" List apps".expandtabs()


# get app
@router.get('/app_id', tags=['apps'], status_code=HTTP_200_OK, summary="Get app with ID", response_model=ReadApp)
async def get(request: Request, app_id: str, db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-apps-list', 'zekoder-zestudio-apps-get'])
    try:
        obj = await AppModel.objects(db)
        result = await obj.get(id=app_id)
        if result:
            return result
        else:
            raise FileNotFoundError
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail={
                "field_name": "{app_id}",
                "message": f"<{app_id}> record not found in  apps"
            })
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, "could not fetch record <{app_id}>")

get.__doc__ = f" Get a specific app by its id".expandtabs()


# query apps
@router.post('/q', tags=['apps'], status_code=HTTP_200_OK, summary="Query apps: Projection, Limit/skips, Sorting, Filters, Joins, Aggregates, Count, Group")
async def query(q: QuerySchema, db: Session = Depends(get_sync_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-apps-list', 'zekoder-zestudio-apps-get'])
    
    try:
        size = q.limit if q.limit else 20
        page = int(q.skip)/size if q.skip else 1
        jq = JSONQ(db, AppModel)
        log.debug(q)
        allowed_aggregates = q.group
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



# create app
@router.post('/', tags=['apps'], status_code=HTTP_201_CREATED, summary="Create new app", response_model=ReadApp)
async def create(request: Request, app: CreateApp, db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-apps-create']) 
    
    try:
        await AppModel.validate_unique_short_name(db, app.short_name)
        new_data = app.dict()
        kwargs = {
            "model_data": new_data,
            "signal_data": {
                "jwt": token.credentials,
                "new_data": new_data,
                "old_data": {},
                "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
            }
        }
        obj = await AppModel.objects(db)
        new_app = await obj.create(**kwargs)
        return new_app
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.args[-1])
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, f"creation of new app failed")

create.__doc__ = f" Create a new app".expandtabs()


# create multiple apps
@router.post('/add-apps', tags=['apps'], status_code=HTTP_201_CREATED, summary="Create multiple apps", response_model=List[ReadApp])
async def create_multiple_apps(request: Request, apps: List[CreateApp], db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-apps-create']) 
    
    new_items, errors_info = [], []
    try:
        for app_index, app in enumerate(apps):
            try:
                await AppModel.validate_unique_short_name(db, app.short_name)
                new_data = app.dict()
                kwargs = {
                    "model_data": new_data,
                    "signal_data": {
                        "jwt": token.credentials,
                        "new_data": new_data,
                        "old_data": {},
                        "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
                    }
                }
                obj = await AppModel.objects(db)
                new_apps = await obj.create(only_add=True, **kwargs)
                new_items.append(new_apps)
            except HTTPException as e:
                errors_info.append({"index": app_index, "errors": e.detail})

        if errors_info:
            return JSONResponse(errors_info, 422)
        return new_items
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.args[-1])
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, f"creation of new apps failed")

create.__doc__ = f" Create multiple new apps".expandtabs()


# upsert multiple apps
@router.post('/upsert-multiple-apps', tags=['apps'], status_code=HTTP_201_CREATED, summary="Upsert multiple apps", response_model=List[ReadApp])
async def upsert_multiple_apps(request: Request, apps: List[UpsertApp], db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-apps-create'])
    new_items, errors_info = [], []
    try:
        for app_index, app in enumerate(apps):
            try:
                await AppModel.validate_unique_short_name(db, app.short_name)
                new_data = app.dict()
                kwargs = {
                    "model_data": new_data,
                    "signal_data": {
                        "jwt": token.credentials,
                        "new_data": new_data,
                        "old_data": {},
                        "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
                    }
                }
                obj = await AppModel.objects(db)
                old_data = await obj.get(id=new_data['id'])
                if old_data:
                    kwargs['signal_data']['old_data'] = dict(old_data.__dict__) if old_data else {}
                    obj = await AppModel.objects(db)
                    updated_apps = await obj.update(obj_id=new_data['id'], **kwargs)
                    new_items.append(updated_apps)
                else:
                    obj = await AppModel.objects(db)
                    new_apps = await obj.create(only_add=True, **kwargs)
                    new_items.append(new_apps)
            except HTTPException as e:
                errors_info.append({"index": app_index, "errors": e.detail})

        if errors_info:
            return JSONResponse(errors_info, 422)
        return new_items
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.args[-1])
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, f"upsert multiple apps failed")

upsert_multiple_apps.__doc__ = f" upsert multiple apps".expandtabs()


# update app
@router.put('/app_id', tags=['apps'], status_code=HTTP_201_CREATED, summary="Update app with ID")
async def update(request: Request, app_id: Union[str, int], app: UpdateApp, db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-apps-update'])
    try:
        await AppModel.validate_unique_short_name(db, app.short_name, app_id)
        obj = await AppModel.objects(db)
        old_data = await obj.get(id=app_id)
        new_data = app.dict(exclude_unset=True)
        kwargs = {
            "model_data": new_data,
            "signal_data": {
                "jwt": token.credentials,
                "new_data": new_data,
                "old_data": dict(old_data.__dict__) if old_data else {},
                "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
            }
        }
        obj = await AppModel.objects(db)
        result = await obj.update(obj_id=app_id, **kwargs)
        return result
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.args[-1])
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, "failed updating session with id <{session_id}>")

update.__doc__ = f" Update a app by its id and payload".expandtabs()


# delete app
@router.delete('/app_id', tags=['apps'], status_code=HTTP_204_NO_CONTENT, summary="Delete app with ID", response_class=Response)
async def delete(request: Request, app_id: Union[str, int], db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-apps-delete'])
    try:
        obj = await AppModel.objects(db)
        old_data = await obj.get(id=app_id)
        kwargs = {
            "model_data": {},
            "signal_data": {
                "jwt": token.credentials,
                "new_data": {},
                "old_data": dict(old_data.__dict__) if old_data else {},
                "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
            }
        }
        obj = await AppModel.objects(db)
        await obj.delete(obj_id=app_id, **kwargs)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail={
                "field_name": "{app_id}",
                "message": f"<{app_id}> record not found in  apps"
            })
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, "failed updating session with id <{session_id}>")

delete.__doc__ = f" Delete a app by its id".expandtabs()


# delete multiple apps
@router.delete('/delete-apps', tags=['apps'], status_code=HTTP_204_NO_CONTENT, summary="Delete multiple apps with IDs", response_class=Response)
async def delete_multiple_apps(request: Request, apps_id: List[str] = QueryParam(), db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-apps-delete'])
    kwargs = {
        "model_data": {},
        "signal_data": {
            "jwt": token.credentials,
            "new_data": {},
            "old_data": {},
            "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
        }
    }
    obj = await AppModel.objects(db)
    await obj.delete_multiple(obj_ids=apps_id, **kwargs)

delete.__doc__ = f" Delete multiple apps by list of ids".expandtabs()

from typing import Union, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response, Query as QueryParam
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from starlette.status import HTTP_204_NO_CONTENT, HTTP_200_OK, HTTP_201_CREATED

from business.app_versions_schema import *
from business.app_versions_model import App_VersionModel

from core.depends import CommonDependencies, get_async_db, get_sync_db, Protect, zeauth_url
from core.logger import log
from core.query import *
from actions import app_version_create, app_version_update
from business.app_versions_model import App_VersionModel


router = APIRouter()


  
# list app_versions
@router.get('/', tags=['app_versions'], status_code=HTTP_200_OK, summary="List app_versions", response_model=ReadApp_Versions)
async def list(request: Request, token: str = Depends(Protect), db: AsyncSession = Depends(get_async_db), commons: CommonDependencies = Depends(CommonDependencies)):
    token.auth(['zekoder-zestudio-app_version-list', 'zekoder-zestudio-app_version-get'])
    try:
        obj = await App_VersionModel.objects(db)
        result = await obj.all(offset=commons.offset, limit=commons.size)
        return {
            'data': result,
            'page_size': commons.size,
            'next_page': int(commons.page) + 1
        }
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, "could not fetch list of app_version")

list.__doc__ = f" List app_versions".expandtabs()


# get app_version
@router.get('/app_version_id', tags=['app_versions'], status_code=HTTP_200_OK, summary="Get app_version with ID", response_model=ReadApp_Version)
async def get(request: Request, app_version_id: str, db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-app_version-list', 'zekoder-zestudio-app_version-get'])
    try:
        obj = await App_VersionModel.objects(db)
        result = await obj.get(id=app_version_id)
        if result:
            return result
        else:
            raise FileNotFoundError
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail={
                "field_name": "{app_version_id}",
                "message": f"<{app_version_id}> record not found in  app_versions"
            })
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, "could not fetch record <{app_version_id}>")

get.__doc__ = f" Get a specific app_version by its id".expandtabs()


# query app_versions
@router.post('/q', tags=['app_versions'], status_code=HTTP_200_OK, summary="Query app_versions: Projection, Limit/skips, Sorting, Filters, Joins, Aggregates, Count, Group")
async def query(q: QuerySchema, db: Session = Depends(get_sync_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-app_versions-list', 'zekoder-zestudio-app_versions-get'])
    
    try:
        size = q.limit if q.limit else 20
        page = int(q.skip)/size if q.skip else 1
        jq = JSONQ(db, App_VersionModel)
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



# create app_version
@router.post('/', tags=['app_versions'], status_code=HTTP_201_CREATED, summary="Create new app_version", response_model=ReadApp_Version)
async def create(request: Request, app_version: CreateApp_Version, db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-app_versions-create']) 
    
    try:
        await App_VersionModel.validate_unique_version_app(db, app_version.version, app_version.app)
        new_data = app_version.dict()
        kwargs = {
            "model_data": new_data,
            "signal_data": {
                "jwt": token.credentials,
                "new_data": new_data,
                "old_data": {},
                "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
            }
        }
        obj = await App_VersionModel.objects(db)
        new_app_version = await obj.create(**kwargs)
        return new_app_version
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.args[-1])
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, f"creation of new app version failed")

create.__doc__ = f" Create a new app_version".expandtabs()


# create multiple app_versions
@router.post('/add-app_versions', tags=['app_versions'], status_code=HTTP_201_CREATED, summary="Create multiple app_versions", response_model=List[ReadApp_Version])
async def create_multiple_app_versions(request: Request, app_versions: List[CreateApp_Version], db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-app_versions-create']) 
    
    new_items, errors_info = [], []
    try:
        for app_version_index, app_version in enumerate(app_versions):
            try:
                await App_VersionModel.validate_unique_version_app(db, app_version.version, app_version.app)
                new_data = app_version.dict()
                kwargs = {
                    "model_data": new_data,
                    "signal_data": {
                        "jwt": token.credentials,
                        "new_data": new_data,
                        "old_data": {},
                        "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
                    }
                }
                obj = await App_VersionModel.objects(db)
                new_app_versions = await obj.create(only_add=True, **kwargs)
                new_items.append(new_app_versions)
            except HTTPException as e:
                errors_info.append({"index": app_version_index, "errors": e.detail})

        if errors_info:
            return JSONResponse(errors_info, 422)
        return new_items
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.args[-1])
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, f"creation of new app versions failed")

create.__doc__ = f" Create multiple new app_versions".expandtabs()


# upsert multiple app_versions
@router.post('/upsert-multiple-app_versions', tags=['app_versions'], status_code=HTTP_201_CREATED, summary="Upsert multiple app_versions", response_model=List[ReadApp_Version])
async def upsert_multiple_app_versions(request: Request, app_versions: List[UpsertApp_Version], db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-app_versions-create'])
    new_items, errors_info = [], []
    try:
        for app_version_index, app_version in enumerate(app_versions):
            try:
                await App_VersionModel.validate_unique_version_app(db, app_version.version, app_version.app)
                new_data = app_version.dict()
                kwargs = {
                    "model_data": new_data,
                    "signal_data": {
                        "jwt": token.credentials,
                        "new_data": new_data,
                        "old_data": {},
                        "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
                    }
                }
                obj = await App_VersionModel.objects(db)
                old_data = await obj.get(id=new_data['id'])
                if old_data:
                    kwargs['signal_data']['old_data'] = dict(old_data.__dict__) if old_data else {}
                    obj = await App_VersionModel.objects(db)
                    updated_app_versions = await obj.update(obj_id=new_data['id'], **kwargs)
                    new_items.append(updated_app_versions)
                else:
                    obj = await App_VersionModel.objects(db)
                    new_app_versions = await obj.create(only_add=True, **kwargs)
                    new_items.append(new_app_versions)
            except HTTPException as e:
                errors_info.append({"index": app_version_index, "errors": e.detail})

        if errors_info:
            return JSONResponse(errors_info, 422)
        return new_items
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.args[-1])
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, f"upsert multiple app versions failed")

upsert_multiple_app_versions.__doc__ = f" upsert multiple app_versions".expandtabs()


# update app_version
@router.put('/app_version_id', tags=['app_versions'], status_code=HTTP_201_CREATED, summary="Update app_version with ID")
async def update(request: Request, app_version_id: Union[str, int], app_version: UpdateApp_Version, db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-app_versions-update'])
    try:
        await App_VersionModel.validate_unique_version_app(db, app_version.version, app_version.app, app_version_id)
        obj = await App_VersionModel.objects(db)
        old_data = await obj.get(id=app_version_id)
        new_data = app_version.dict(exclude_unset=True)
        kwargs = {
            "model_data": new_data,
            "signal_data": {
                "jwt": token.credentials,
                "new_data": new_data,
                "old_data": dict(old_data.__dict__) if old_data else {},
                "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
            }
        }
        obj = await App_VersionModel.objects(db)
        result = await obj.update(obj_id=app_version_id, **kwargs)
        return result
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.args[-1])
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, "failed updating session with id <{session_id}>")

update.__doc__ = f" Update a app_version by its id and payload".expandtabs()


# delete app_version
@router.delete('/app_version_id', tags=['app_versions'], status_code=HTTP_204_NO_CONTENT, summary="Delete app_version with ID", response_class=Response)
async def delete(request: Request, app_version_id: Union[str, int], db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-app_versions-delete'])
    try:
        obj = await App_VersionModel.objects(db)
        old_data = await obj.get(id=app_version_id)
        kwargs = {
            "model_data": {},
            "signal_data": {
                "jwt": token.credentials,
                "new_data": {},
                "old_data": dict(old_data.__dict__) if old_data else {},
                "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
            }
        }
        obj = await App_VersionModel.objects(db)
        await obj.delete(obj_id=app_version_id, **kwargs)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail={
                "field_name": "{app_version_id}",
                "message": f"<{app_version_id}> record not found in  app_versions"
            })
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, "failed updating session with id <{session_id}>")

delete.__doc__ = f" Delete a app_version by its id".expandtabs()


# delete multiple app_versions
@router.delete('/delete-app_versions', tags=['app_versions'], status_code=HTTP_204_NO_CONTENT, summary="Delete multiple app_versions with IDs", response_class=Response)
async def delete_multiple_app_versions(request: Request, app_versions_id: List[str] = QueryParam(), db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-app_versions-delete'])
    kwargs = {
        "model_data": {},
        "signal_data": {
            "jwt": token.credentials,
            "new_data": {},
            "old_data": {},
            "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
        }
    }
    obj = await App_VersionModel.objects(db)
    await obj.delete_multiple(obj_ids=app_versions_id, **kwargs)

delete.__doc__ = f" Delete multiple app_versions by list of ids".expandtabs()

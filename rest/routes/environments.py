from typing import Union, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response, Query as QueryParam
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from starlette.status import HTTP_204_NO_CONTENT, HTTP_200_OK, HTTP_201_CREATED

from business.environments_schema import *
from business.environments_model import EnvironmentModel

from core.depends import CommonDependencies, get_async_db, get_sync_db, Protect, zeauth_url
from core.logger import log
from core.query import *

from business.environments_model import EnvironmentModel


router = APIRouter()


  
# list environments
@router.get('/', tags=['environments'], status_code=HTTP_200_OK, summary="List environments", response_model=ReadEnvironments)
async def list(request: Request, token: str = Depends(Protect), db: AsyncSession = Depends(get_async_db), commons: CommonDependencies = Depends(CommonDependencies)):
    token.auth(['zekoder-zestudio-environments-list', 'zekoder-zestudio-environments-get'])
    try:
        obj = await EnvironmentModel.objects(db)
        result = await obj.all(offset=commons.offset, limit=commons.size)
        return {
            'data': result,
            'page_size': commons.size,
            'next_page': int(commons.page) + 1
        }
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, "could not fetch list of environment")

list.__doc__ = f" List environments".expandtabs()


# get environment
@router.get('/environment_id', tags=['environments'], status_code=HTTP_200_OK, summary="Get environment with ID", response_model=ReadEnvironment)
async def get(request: Request, environment_id: str, db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-environments-list', 'zekoder-zestudio-environments-get'])
    try:
        obj = await EnvironmentModel.objects(db)
        result = await obj.get(id=environment_id)
        if result:
            return result
        else:
            raise FileNotFoundError
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail={
                "field_name": "{environment_id}",
                "message": f"<{environment_id}> record not found in  environments"
            })
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, "could not fetch record <{environment_id}>")

get.__doc__ = f" Get a specific environment by its id".expandtabs()


# query environments
@router.post('/q', tags=['environments'], status_code=HTTP_200_OK, summary="Query environments: Projection, Limit/skips, Sorting, Filters, Joins, Aggregates, Count, Group")
async def query(q: QuerySchema, db: Session = Depends(get_sync_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-environments-list', 'zekoder-zestudio-environments-get'])
    
    try:
        size = q.limit if q.limit else 20
        page = int(q.skip)/size if q.skip else 1
        jq = JSONQ(db, EnvironmentModel)
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



# create environment
@router.post('/', tags=['environments'], status_code=HTTP_201_CREATED, summary="Create new environment", response_model=ReadEnvironment)
async def create(request: Request, environment: CreateEnvironment, db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-environments-create']) 
    
    try:
        await EnvironmentModel.validate_unique_name(db, environment.name)
        new_data = environment.dict()
        kwargs = {
            "model_data": new_data,
            "signal_data": {
                "jwt": token.credentials,
                "new_data": new_data,
                "old_data": {},
                "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
            }
        }
        obj = await EnvironmentModel.objects(db)
        new_environment = await obj.create(**kwargs)
        return new_environment
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.args[-1])
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, f"creation of new environment failed")

create.__doc__ = f" Create a new environment".expandtabs()


# create multiple environments
@router.post('/add-environments', tags=['environments'], status_code=HTTP_201_CREATED, summary="Create multiple environments", response_model=List[ReadEnvironment])
async def create_multiple_environments(request: Request, environments: List[CreateEnvironment], db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-environments-create']) 
    
    new_items, errors_info = [], []
    try:
        for environment_index, environment in enumerate(environments):
            try:
                await EnvironmentModel.validate_unique_name(db, environment.name)
                new_data = environment.dict()
                kwargs = {
                    "model_data": new_data,
                    "signal_data": {
                        "jwt": token.credentials,
                        "new_data": new_data,
                        "old_data": {},
                        "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
                    }
                }
                obj = await EnvironmentModel.objects(db)
                new_environments = await obj.create(only_add=True, **kwargs)
                new_items.append(new_environments)
            except HTTPException as e:
                errors_info.append({"index": environment_index, "errors": e.detail})

        if errors_info:
            return JSONResponse(errors_info, 422)
        return new_items
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.args[-1])
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, f"creation of new environments failed")

create.__doc__ = f" Create multiple new environments".expandtabs()


# upsert multiple environments
@router.post('/upsert-multiple-environments', tags=['environments'], status_code=HTTP_201_CREATED, summary="Upsert multiple environments", response_model=List[ReadEnvironment])
async def upsert_multiple_environments(request: Request, environments: List[UpsertEnvironment], db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-environments-create'])
    new_items, errors_info = [], []
    try:
        for environment_index, environment in enumerate(environments):
            try:
                await EnvironmentModel.validate_unique_name(db, environment.name)
                new_data = environment.dict()
                kwargs = {
                    "model_data": new_data,
                    "signal_data": {
                        "jwt": token.credentials,
                        "new_data": new_data,
                        "old_data": {},
                        "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
                    }
                }
                obj = await EnvironmentModel.objects(db)
                old_data = await obj.get(id=new_data['id'])
                if old_data:
                    kwargs['signal_data']['old_data'] = dict(old_data.__dict__) if old_data else {}
                    obj = await EnvironmentModel.objects(db)
                    updated_environments = await obj.update(obj_id=new_data['id'], **kwargs)
                    new_items.append(updated_environments)
                else:
                    obj = await EnvironmentModel.objects(db)
                    new_environments = await obj.create(only_add=True, **kwargs)
                    new_items.append(new_environments)
            except HTTPException as e:
                errors_info.append({"index": environment_index, "errors": e.detail})

        if errors_info:
            return JSONResponse(errors_info, 422)
        return new_items
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.args[-1])
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, f"upsert multiple environments failed")

upsert_multiple_environments.__doc__ = f" upsert multiple environments".expandtabs()


# update environment
@router.put('/environment_id', tags=['environments'], status_code=HTTP_201_CREATED, summary="Update environment with ID")
async def update(request: Request, environment_id: Union[str, int], environment: UpdateEnvironment, db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-environments-update'])
    try:
        await EnvironmentModel.validate_unique_name(db, environment.name, environment_id)
        obj = await EnvironmentModel.objects(db)
        old_data = await obj.get(id=environment_id)
        new_data = environment.dict(exclude_unset=True)
        kwargs = {
            "model_data": new_data,
            "signal_data": {
                "jwt": token.credentials,
                "new_data": new_data,
                "old_data": dict(old_data.__dict__) if old_data else {},
                "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
            }
        }
        obj = await EnvironmentModel.objects(db)
        result = await obj.update(obj_id=environment_id, **kwargs)
        return result
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.args[-1])
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, "failed updating session with id <{session_id}>")

update.__doc__ = f" Update a environment by its id and payload".expandtabs()


# delete environment
@router.delete('/environment_id', tags=['environments'], status_code=HTTP_204_NO_CONTENT, summary="Delete environment with ID", response_class=Response)
async def delete(request: Request, environment_id: Union[str, int], db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-environments-delete'])
    try:
        obj = await EnvironmentModel.objects(db)
        old_data = await obj.get(id=environment_id)
        kwargs = {
            "model_data": {},
            "signal_data": {
                "jwt": token.credentials,
                "new_data": {},
                "old_data": dict(old_data.__dict__) if old_data else {},
                "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
            }
        }
        obj = await EnvironmentModel.objects(db)
        await obj.delete(obj_id=environment_id, **kwargs)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail={
                "field_name": "{environment_id}",
                "message": f"<{environment_id}> record not found in  environments"
            })
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, "failed updating session with id <{session_id}>")

delete.__doc__ = f" Delete a environment by its id".expandtabs()


# delete multiple environments
@router.delete('/delete-environments', tags=['environments'], status_code=HTTP_204_NO_CONTENT, summary="Delete multiple environments with IDs", response_class=Response)
async def delete_multiple_environments(request: Request, environments_id: List[str] = QueryParam(), db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-environments-delete'])
    kwargs = {
        "model_data": {},
        "signal_data": {
            "jwt": token.credentials,
            "new_data": {},
            "old_data": {},
            "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
        }
    }
    obj = await EnvironmentModel.objects(db)
    await obj.delete_multiple(obj_ids=environments_id, **kwargs)

delete.__doc__ = f" Delete multiple environments by list of ids".expandtabs()

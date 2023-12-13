from typing import Union, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response, Query as QueryParam
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from starlette.status import HTTP_204_NO_CONTENT, HTTP_200_OK, HTTP_201_CREATED

from business.integrations_schema import *
from business.integrations_model import IntegrationModel

from core.depends import CommonDependencies, get_async_db, get_sync_db, Protect, zeauth_url
from core.logger import log
from core.query import *

from business.integrations_model import IntegrationModel


router = APIRouter()


  
# list integrations
@router.get('/', tags=['integrations'], status_code=HTTP_200_OK, summary="List integrations", response_model=ReadIntegrations)
async def list(request: Request, token: str = Depends(Protect), db: AsyncSession = Depends(get_async_db), commons: CommonDependencies = Depends(CommonDependencies)):
    token.auth(['zekoder-zestudio-integrations-list', 'zekoder-zestudio-integrations-get'])
    try:
        obj = await IntegrationModel.objects(db)
        result = await obj.all(offset=commons.offset, limit=commons.size)
        return {
            'data': result,
            'page_size': commons.size,
            'next_page': int(commons.page) + 1
        }
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, "could not fetch list of integration")

list.__doc__ = f" List integrations".expandtabs()


# get integration
@router.get('/integration_id', tags=['integrations'], status_code=HTTP_200_OK, summary="Get integration with ID", response_model=ReadIntegration)
async def get(request: Request, integration_id: str, db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-integrations-list', 'zekoder-zestudio-integrations-get'])
    try:
        obj = await IntegrationModel.objects(db)
        result = await obj.get(id=integration_id)
        if result:
            return result
        else:
            raise FileNotFoundError
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail={
                "field_name": "{integration_id}",
                "message": f"<{integration_id}> record not found in  integrations"
            })
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, "could not fetch record <{integration_id}>")

get.__doc__ = f" Get a specific integration by its id".expandtabs()


# query integrations
@router.post('/q', tags=['integrations'], status_code=HTTP_200_OK, summary="Query integrations: Projection, Limit/skips, Sorting, Filters, Joins, Aggregates, Count, Group")
async def query(q: QuerySchema, db: Session = Depends(get_sync_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-integrations-list', 'zekoder-zestudio-integrations-get'])
    
    try:
        size = q.limit if q.limit else 20
        page = int(q.skip)/size if q.skip else 1
        jq = JSONQ(db, IntegrationModel)
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



# create integration
@router.post('/', tags=['integrations'], status_code=HTTP_201_CREATED, summary="Create new integration", response_model=ReadIntegration)
async def create(request: Request, integration: CreateIntegration, db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-integrations-create']) 
    
    try:
        await IntegrationModel.validate_unique_name_provider(db, integration.name, integration.provider)
        new_data = integration.dict()
        kwargs = {
            "model_data": new_data,
            "signal_data": {
                "jwt": token.credentials,
                "new_data": new_data,
                "old_data": {},
                "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
            }
        }
        obj = await IntegrationModel.objects(db)
        new_integration = await obj.create(**kwargs)
        return new_integration
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.args[-1])
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, f"creation of new integration failed")

create.__doc__ = f" Create a new integration".expandtabs()


# create multiple integrations
@router.post('/add-integrations', tags=['integrations'], status_code=HTTP_201_CREATED, summary="Create multiple integrations", response_model=List[ReadIntegration])
async def create_multiple_integrations(request: Request, integrations: List[CreateIntegration], db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-integrations-create']) 
    
    new_items, errors_info = [], []
    try:
        for integration_index, integration in enumerate(integrations):
            try:
                await IntegrationModel.validate_unique_name_provider(db, integration.name, integration.provider)
                new_data = integration.dict()
                kwargs = {
                    "model_data": new_data,
                    "signal_data": {
                        "jwt": token.credentials,
                        "new_data": new_data,
                        "old_data": {},
                        "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
                    }
                }
                obj = await IntegrationModel.objects(db)
                new_integrations = await obj.create(only_add=True, **kwargs)
                new_items.append(new_integrations)
            except HTTPException as e:
                errors_info.append({"index": integration_index, "errors": e.detail})

        if errors_info:
            return JSONResponse(errors_info, 422)
        return new_items
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.args[-1])
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, f"creation of new integrations failed")

create.__doc__ = f" Create multiple new integrations".expandtabs()


# upsert multiple integrations
@router.post('/upsert-multiple-integrations', tags=['integrations'], status_code=HTTP_201_CREATED, summary="Upsert multiple integrations", response_model=List[ReadIntegration])
async def upsert_multiple_integrations(request: Request, integrations: List[UpsertIntegration], db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-integrations-create'])
    new_items, errors_info = [], []
    try:
        for integration_index, integration in enumerate(integrations):
            try:
                await IntegrationModel.validate_unique_name_provider(db, integration.name, integration.provider)
                new_data = integration.dict()
                kwargs = {
                    "model_data": new_data,
                    "signal_data": {
                        "jwt": token.credentials,
                        "new_data": new_data,
                        "old_data": {},
                        "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
                    }
                }
                obj = await IntegrationModel.objects(db)
                old_data = await obj.get(id=new_data['id'])
                if old_data:
                    kwargs['signal_data']['old_data'] = dict(old_data.__dict__) if old_data else {}
                    obj = await IntegrationModel.objects(db)
                    updated_integrations = await obj.update(obj_id=new_data['id'], **kwargs)
                    new_items.append(updated_integrations)
                else:
                    obj = await IntegrationModel.objects(db)
                    new_integrations = await obj.create(only_add=True, **kwargs)
                    new_items.append(new_integrations)
            except HTTPException as e:
                errors_info.append({"index": integration_index, "errors": e.detail})

        if errors_info:
            return JSONResponse(errors_info, 422)
        return new_items
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.args[-1])
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, f"upsert multiple integrations failed")

upsert_multiple_integrations.__doc__ = f" upsert multiple integrations".expandtabs()


# update integration
@router.put('/integration_id', tags=['integrations'], status_code=HTTP_201_CREATED, summary="Update integration with ID")
async def update(request: Request, integration_id: Union[str, int], integration: UpdateIntegration, db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-integrations-update'])
    try:
        await IntegrationModel.validate_unique_name_provider(db, integration.name, integration.provider, integration_id)
        obj = await IntegrationModel.objects(db)
        old_data = await obj.get(id=integration_id)
        new_data = integration.dict(exclude_unset=True)
        kwargs = {
            "model_data": new_data,
            "signal_data": {
                "jwt": token.credentials,
                "new_data": new_data,
                "old_data": dict(old_data.__dict__) if old_data else {},
                "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
            }
        }
        obj = await IntegrationModel.objects(db)
        result = await obj.update(obj_id=integration_id, **kwargs)
        return result
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.args[-1])
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, "failed updating session with id <{session_id}>")

update.__doc__ = f" Update a integration by its id and payload".expandtabs()


# delete integration
@router.delete('/integration_id', tags=['integrations'], status_code=HTTP_204_NO_CONTENT, summary="Delete integration with ID", response_class=Response)
async def delete(request: Request, integration_id: Union[str, int], db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-integrations-delete'])
    try:
        obj = await IntegrationModel.objects(db)
        old_data = await obj.get(id=integration_id)
        kwargs = {
            "model_data": {},
            "signal_data": {
                "jwt": token.credentials,
                "new_data": {},
                "old_data": dict(old_data.__dict__) if old_data else {},
                "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
            }
        }
        obj = await IntegrationModel.objects(db)
        await obj.delete(obj_id=integration_id, **kwargs)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail={
                "field_name": "{integration_id}",
                "message": f"<{integration_id}> record not found in  integrations"
            })
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, "failed updating session with id <{session_id}>")

delete.__doc__ = f" Delete a integration by its id".expandtabs()


# delete multiple integrations
@router.delete('/delete-integrations', tags=['integrations'], status_code=HTTP_204_NO_CONTENT, summary="Delete multiple integrations with IDs", response_class=Response)
async def delete_multiple_integrations(request: Request, integrations_id: List[str] = QueryParam(), db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-integrations-delete'])
    kwargs = {
        "model_data": {},
        "signal_data": {
            "jwt": token.credentials,
            "new_data": {},
            "old_data": {},
            "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
        }
    }
    obj = await IntegrationModel.objects(db)
    await obj.delete_multiple(obj_ids=integrations_id, **kwargs)

delete.__doc__ = f" Delete multiple integrations by list of ids".expandtabs()

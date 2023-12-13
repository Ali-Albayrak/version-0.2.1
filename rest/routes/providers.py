from typing import Union, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response, Query as QueryParam
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from starlette.status import HTTP_204_NO_CONTENT, HTTP_200_OK, HTTP_201_CREATED

from business.providers_schema import *
from business.providers_model import ProviderModel

from core.depends import CommonDependencies, get_async_db, get_sync_db, Protect, zeauth_url
from core.logger import log
from core.query import *

from business.providers_model import ProviderModel


router = APIRouter()


  
# list providers
@router.get('/', tags=['providers'], status_code=HTTP_200_OK, summary="List providers", response_model=ReadProviders)
async def list(request: Request, token: str = Depends(Protect), db: AsyncSession = Depends(get_async_db), commons: CommonDependencies = Depends(CommonDependencies)):
    token.auth(['zekoder-zestudio-providers-list', 'zekoder-zestudio-providers-get'])
    try:
        obj = await ProviderModel.objects(db)
        result = await obj.all(offset=commons.offset, limit=commons.size)
        return {
            'data': result,
            'page_size': commons.size,
            'next_page': int(commons.page) + 1
        }
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, "could not fetch list of provider")

list.__doc__ = f" List providers".expandtabs()


# get provider
@router.get('/provider_id', tags=['providers'], status_code=HTTP_200_OK, summary="Get provider with ID", response_model=ReadProvider)
async def get(request: Request, provider_id: str, db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-providers-list', 'zekoder-zestudio-providers-get'])
    try:
        obj = await ProviderModel.objects(db)
        result = await obj.get(id=provider_id)
        if result:
            return result
        else:
            raise FileNotFoundError
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail={
                "field_name": "{provider_id}",
                "message": f"<{provider_id}> record not found in  providers"
            })
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, "could not fetch record <{provider_id}>")

get.__doc__ = f" Get a specific provider by its id".expandtabs()


# query providers
@router.post('/q', tags=['providers'], status_code=HTTP_200_OK, summary="Query providers: Projection, Limit/skips, Sorting, Filters, Joins, Aggregates, Count, Group")
async def query(q: QuerySchema, db: Session = Depends(get_sync_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-providers-list', 'zekoder-zestudio-providers-get'])
    
    try:
        size = q.limit if q.limit else 20
        page = int(q.skip)/size if q.skip else 1
        jq = JSONQ(db, ProviderModel)
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



# create provider
@router.post('/', tags=['providers'], status_code=HTTP_201_CREATED, summary="Create new provider", response_model=ReadProvider)
async def create(request: Request, provider: CreateProvider, db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-providers-create']) 
    
    try:
        await ProviderModel.validate_unique_short_name(db, provider.short_name)
        new_data = provider.dict()
        kwargs = {
            "model_data": new_data,
            "signal_data": {
                "jwt": token.credentials,
                "new_data": new_data,
                "old_data": {},
                "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
            }
        }
        obj = await ProviderModel.objects(db)
        new_provider = await obj.create(**kwargs)
        return new_provider
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.args[-1])
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, f"creation of new provider failed")

create.__doc__ = f" Create a new provider".expandtabs()


# create multiple providers
@router.post('/add-providers', tags=['providers'], status_code=HTTP_201_CREATED, summary="Create multiple providers", response_model=List[ReadProvider])
async def create_multiple_providers(request: Request, providers: List[CreateProvider], db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-providers-create']) 
    
    new_items, errors_info = [], []
    try:
        for provider_index, provider in enumerate(providers):
            try:
                await ProviderModel.validate_unique_short_name(db, provider.short_name)
                new_data = provider.dict()
                kwargs = {
                    "model_data": new_data,
                    "signal_data": {
                        "jwt": token.credentials,
                        "new_data": new_data,
                        "old_data": {},
                        "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
                    }
                }
                obj = await ProviderModel.objects(db)
                new_providers = await obj.create(only_add=True, **kwargs)
                new_items.append(new_providers)
            except HTTPException as e:
                errors_info.append({"index": provider_index, "errors": e.detail})

        if errors_info:
            return JSONResponse(errors_info, 422)
        return new_items
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.args[-1])
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, f"creation of new providers failed")

create.__doc__ = f" Create multiple new providers".expandtabs()


# upsert multiple providers
@router.post('/upsert-multiple-providers', tags=['providers'], status_code=HTTP_201_CREATED, summary="Upsert multiple providers", response_model=List[ReadProvider])
async def upsert_multiple_providers(request: Request, providers: List[UpsertProvider], db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-providers-create'])
    new_items, errors_info = [], []
    try:
        for provider_index, provider in enumerate(providers):
            try:
                await ProviderModel.validate_unique_short_name(db, provider.short_name)
                new_data = provider.dict()
                kwargs = {
                    "model_data": new_data,
                    "signal_data": {
                        "jwt": token.credentials,
                        "new_data": new_data,
                        "old_data": {},
                        "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
                    }
                }
                obj = await ProviderModel.objects(db)
                old_data = await obj.get(id=new_data['id'])
                if old_data:
                    kwargs['signal_data']['old_data'] = dict(old_data.__dict__) if old_data else {}
                    obj = await ProviderModel.objects(db)
                    updated_providers = await obj.update(obj_id=new_data['id'], **kwargs)
                    new_items.append(updated_providers)
                else:
                    obj = await ProviderModel.objects(db)
                    new_providers = await obj.create(only_add=True, **kwargs)
                    new_items.append(new_providers)
            except HTTPException as e:
                errors_info.append({"index": provider_index, "errors": e.detail})

        if errors_info:
            return JSONResponse(errors_info, 422)
        return new_items
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.args[-1])
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, f"upsert multiple providers failed")

upsert_multiple_providers.__doc__ = f" upsert multiple providers".expandtabs()


# update provider
@router.put('/provider_id', tags=['providers'], status_code=HTTP_201_CREATED, summary="Update provider with ID")
async def update(request: Request, provider_id: Union[str, int], provider: UpdateProvider, db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-providers-update'])
    try:
        await ProviderModel.validate_unique_short_name(db, provider.short_name, provider_id)
        obj = await ProviderModel.objects(db)
        old_data = await obj.get(id=provider_id)
        new_data = provider.dict(exclude_unset=True)
        kwargs = {
            "model_data": new_data,
            "signal_data": {
                "jwt": token.credentials,
                "new_data": new_data,
                "old_data": dict(old_data.__dict__) if old_data else {},
                "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
            }
        }
        obj = await ProviderModel.objects(db)
        result = await obj.update(obj_id=provider_id, **kwargs)
        return result
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.args[-1])
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, "failed updating session with id <{session_id}>")

update.__doc__ = f" Update a provider by its id and payload".expandtabs()


# delete provider
@router.delete('/provider_id', tags=['providers'], status_code=HTTP_204_NO_CONTENT, summary="Delete provider with ID", response_class=Response)
async def delete(request: Request, provider_id: Union[str, int], db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-providers-delete'])
    try:
        obj = await ProviderModel.objects(db)
        old_data = await obj.get(id=provider_id)
        kwargs = {
            "model_data": {},
            "signal_data": {
                "jwt": token.credentials,
                "new_data": {},
                "old_data": dict(old_data.__dict__) if old_data else {},
                "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
            }
        }
        obj = await ProviderModel.objects(db)
        await obj.delete(obj_id=provider_id, **kwargs)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail={
                "field_name": "{provider_id}",
                "message": f"<{provider_id}> record not found in  providers"
            })
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, "failed updating session with id <{session_id}>")

delete.__doc__ = f" Delete a provider by its id".expandtabs()


# delete multiple providers
@router.delete('/delete-providers', tags=['providers'], status_code=HTTP_204_NO_CONTENT, summary="Delete multiple providers with IDs", response_class=Response)
async def delete_multiple_providers(request: Request, providers_id: List[str] = QueryParam(), db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-providers-delete'])
    kwargs = {
        "model_data": {},
        "signal_data": {
            "jwt": token.credentials,
            "new_data": {},
            "old_data": {},
            "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
        }
    }
    obj = await ProviderModel.objects(db)
    await obj.delete_multiple(obj_ids=providers_id, **kwargs)

delete.__doc__ = f" Delete multiple providers by list of ids".expandtabs()

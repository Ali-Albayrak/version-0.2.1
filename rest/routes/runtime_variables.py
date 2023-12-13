from typing import Union, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response, Query as QueryParam
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from starlette.status import HTTP_204_NO_CONTENT, HTTP_200_OK, HTTP_201_CREATED

from business.runtime_variables_schema import *
from business.runtime_variables_model import Runtime_VariableModel

from core.depends import CommonDependencies, get_async_db, get_sync_db, Protect, zeauth_url
from core.logger import log
from core.query import *

from business.runtime_variables_model import Runtime_VariableModel


router = APIRouter()


  
# list runtime_variables
@router.get('/', tags=['runtime_variables'], status_code=HTTP_200_OK, summary="List runtime_variables", response_model=ReadRuntime_Variables)
async def list(request: Request, token: str = Depends(Protect), db: AsyncSession = Depends(get_async_db), commons: CommonDependencies = Depends(CommonDependencies)):
    token.auth(['zekoder-zestudio-runtime_variables-list', 'zekoder-zestudio-runtime_variables-get'])
    try:
        obj = await Runtime_VariableModel.objects(db)
        result = await obj.all(offset=commons.offset, limit=commons.size)
        return {
            'data': result,
            'page_size': commons.size,
            'next_page': int(commons.page) + 1
        }
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, "could not fetch list of runtime_variable")

list.__doc__ = f" List runtime_variables".expandtabs()


# get runtime_variable
@router.get('/runtime_variable_id', tags=['runtime_variables'], status_code=HTTP_200_OK, summary="Get runtime_variable with ID", response_model=ReadRuntime_Variable)
async def get(request: Request, runtime_variable_id: str, db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-runtime_variables-list', 'zekoder-zestudio-runtime_variables-get'])
    try:
        obj = await Runtime_VariableModel.objects(db)
        result = await obj.get(id=runtime_variable_id)
        if result:
            return result
        else:
            raise FileNotFoundError
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail={
                "field_name": "{runtime_variable_id}",
                "message": f"<{runtime_variable_id}> record not found in  runtime_variables"
            })
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, "could not fetch record <{runtime_variable_id}>")

get.__doc__ = f" Get a specific runtime_variable by its id".expandtabs()


# query runtime_variables
@router.post('/q', tags=['runtime_variables'], status_code=HTTP_200_OK, summary="Query runtime_variables: Projection, Limit/skips, Sorting, Filters, Joins, Aggregates, Count, Group")
async def query(q: QuerySchema, db: Session = Depends(get_sync_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-runtime_variables-list', 'zekoder-zestudio-runtime_variables-get'])
    
    try:
        size = q.limit if q.limit else 20
        page = int(q.skip)/size if q.skip else 1
        jq = JSONQ(db, Runtime_VariableModel)
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



# create runtime_variable
@router.post('/', tags=['runtime_variables'], status_code=HTTP_201_CREATED, summary="Create new runtime_variable", response_model=ReadRuntime_Variable)
async def create(request: Request, runtime_variable: CreateRuntime_Variable, db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-runtime_variables-create']) 
    
    try:
        await Runtime_VariableModel.validate_unique_app_solution(db, runtime_variable.app, runtime_variable.solution)
        new_data = runtime_variable.dict()
        kwargs = {
            "model_data": new_data,
            "signal_data": {
                "jwt": token.credentials,
                "new_data": new_data,
                "old_data": {},
                "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
            }
        }
        obj = await Runtime_VariableModel.objects(db)
        new_runtime_variable = await obj.create(**kwargs)
        return new_runtime_variable
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.args[-1])
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, f"creation of new runtime variable failed")

create.__doc__ = f" Create a new runtime_variable".expandtabs()


# create multiple runtime_variables
@router.post('/add-runtime_variables', tags=['runtime_variables'], status_code=HTTP_201_CREATED, summary="Create multiple runtime_variables", response_model=List[ReadRuntime_Variable])
async def create_multiple_runtime_variables(request: Request, runtime_variables: List[CreateRuntime_Variable], db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-runtime_variables-create']) 
    
    new_items, errors_info = [], []
    try:
        for runtime_variable_index, runtime_variable in enumerate(runtime_variables):
            try:
                await Runtime_VariableModel.validate_unique_app_solution(db, runtime_variable.app, runtime_variable.solution)
                new_data = runtime_variable.dict()
                kwargs = {
                    "model_data": new_data,
                    "signal_data": {
                        "jwt": token.credentials,
                        "new_data": new_data,
                        "old_data": {},
                        "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
                    }
                }
                obj = await Runtime_VariableModel.objects(db)
                new_runtime_variables = await obj.create(only_add=True, **kwargs)
                new_items.append(new_runtime_variables)
            except HTTPException as e:
                errors_info.append({"index": runtime_variable_index, "errors": e.detail})

        if errors_info:
            return JSONResponse(errors_info, 422)
        return new_items
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.args[-1])
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, f"creation of new runtime variables failed")

create.__doc__ = f" Create multiple new runtime_variables".expandtabs()


# upsert multiple runtime_variables
@router.post('/upsert-multiple-runtime_variables', tags=['runtime_variables'], status_code=HTTP_201_CREATED, summary="Upsert multiple runtime_variables", response_model=List[ReadRuntime_Variable])
async def upsert_multiple_runtime_variables(request: Request, runtime_variables: List[UpsertRuntime_Variable], db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-runtime_variables-create'])
    new_items, errors_info = [], []
    try:
        for runtime_variable_index, runtime_variable in enumerate(runtime_variables):
            try:
                await Runtime_VariableModel.validate_unique_app_solution(db, runtime_variable.app, runtime_variable.solution)
                new_data = runtime_variable.dict()
                kwargs = {
                    "model_data": new_data,
                    "signal_data": {
                        "jwt": token.credentials,
                        "new_data": new_data,
                        "old_data": {},
                        "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
                    }
                }
                obj = await Runtime_VariableModel.objects(db)
                old_data = await obj.get(id=new_data['id'])
                if old_data:
                    kwargs['signal_data']['old_data'] = dict(old_data.__dict__) if old_data else {}
                    obj = await Runtime_VariableModel.objects(db)
                    updated_runtime_variables = await obj.update(obj_id=new_data['id'], **kwargs)
                    new_items.append(updated_runtime_variables)
                else:
                    obj = await Runtime_VariableModel.objects(db)
                    new_runtime_variables = await obj.create(only_add=True, **kwargs)
                    new_items.append(new_runtime_variables)
            except HTTPException as e:
                errors_info.append({"index": runtime_variable_index, "errors": e.detail})

        if errors_info:
            return JSONResponse(errors_info, 422)
        return new_items
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.args[-1])
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, f"upsert multiple runtime variables failed")

upsert_multiple_runtime_variables.__doc__ = f" upsert multiple runtime_variables".expandtabs()


# update runtime_variable
@router.put('/runtime_variable_id', tags=['runtime_variables'], status_code=HTTP_201_CREATED, summary="Update runtime_variable with ID")
async def update(request: Request, runtime_variable_id: Union[str, int], runtime_variable: UpdateRuntime_Variable, db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-runtime_variables-update'])
    try:
        await Runtime_VariableModel.validate_unique_app_solution(db, runtime_variable.app, runtime_variable.solution, runtime_variable_id)
        obj = await Runtime_VariableModel.objects(db)
        old_data = await obj.get(id=runtime_variable_id)
        new_data = runtime_variable.dict(exclude_unset=True)
        kwargs = {
            "model_data": new_data,
            "signal_data": {
                "jwt": token.credentials,
                "new_data": new_data,
                "old_data": dict(old_data.__dict__) if old_data else {},
                "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
            }
        }
        obj = await Runtime_VariableModel.objects(db)
        result = await obj.update(obj_id=runtime_variable_id, **kwargs)
        return result
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.args[-1])
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, "failed updating session with id <{session_id}>")

update.__doc__ = f" Update a runtime_variable by its id and payload".expandtabs()


# delete runtime_variable
@router.delete('/runtime_variable_id', tags=['runtime_variables'], status_code=HTTP_204_NO_CONTENT, summary="Delete runtime_variable with ID", response_class=Response)
async def delete(request: Request, runtime_variable_id: Union[str, int], db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-runtime_variables-delete'])
    try:
        obj = await Runtime_VariableModel.objects(db)
        old_data = await obj.get(id=runtime_variable_id)
        kwargs = {
            "model_data": {},
            "signal_data": {
                "jwt": token.credentials,
                "new_data": {},
                "old_data": dict(old_data.__dict__) if old_data else {},
                "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
            }
        }
        obj = await Runtime_VariableModel.objects(db)
        await obj.delete(obj_id=runtime_variable_id, **kwargs)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail={
                "field_name": "{runtime_variable_id}",
                "message": f"<{runtime_variable_id}> record not found in  runtime_variables"
            })
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, "failed updating session with id <{session_id}>")

delete.__doc__ = f" Delete a runtime_variable by its id".expandtabs()


# delete multiple runtime_variables
@router.delete('/delete-runtime_variables', tags=['runtime_variables'], status_code=HTTP_204_NO_CONTENT, summary="Delete multiple runtime_variables with IDs", response_class=Response)
async def delete_multiple_runtime_variables(request: Request, runtime_variables_id: List[str] = QueryParam(), db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-runtime_variables-delete'])
    kwargs = {
        "model_data": {},
        "signal_data": {
            "jwt": token.credentials,
            "new_data": {},
            "old_data": {},
            "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
        }
    }
    obj = await Runtime_VariableModel.objects(db)
    await obj.delete_multiple(obj_ids=runtime_variables_id, **kwargs)

delete.__doc__ = f" Delete multiple runtime_variables by list of ids".expandtabs()

from typing import Union, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response, Query as QueryParam
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from starlette.status import HTTP_204_NO_CONTENT, HTTP_200_OK, HTTP_201_CREATED

from business.apps__solutions_schema import *
from business.apps__solutions_model import App__SolutionModel

from core.depends import CommonDependencies, get_async_db, get_sync_db, Protect, zeauth_url
from core.logger import log
from core.query import *

from business.apps__solutions_model import App__SolutionModel


router = APIRouter()


  
# list apps__solutions
@router.get('/', tags=['apps__solutions'], status_code=HTTP_200_OK, summary="List apps__solutions", response_model=ReadApps__Solutions)
async def list(request: Request, token: str = Depends(Protect), db: AsyncSession = Depends(get_async_db), commons: CommonDependencies = Depends(CommonDependencies)):
    token.auth(['zekoder-zestudio-apps__solutions-list', 'zekoder-zestudio-apps__solutions-get'])
    try:
        obj = await App__SolutionModel.objects(db)
        result = await obj.all(offset=commons.offset, limit=commons.size)
        return {
            'data': result,
            'page_size': commons.size,
            'next_page': int(commons.page) + 1
        }
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, "could not fetch list of app__solution")

list.__doc__ = f" List apps__solutions".expandtabs()


# get app__solution
@router.get('/app__solution_id', tags=['apps__solutions'], status_code=HTTP_200_OK, summary="Get app__solution with ID", response_model=ReadApp__Solution)
async def get(request: Request, app__solution_id: str, db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-apps__solutions-list', 'zekoder-zestudio-apps__solutions-get'])
    try:
        obj = await App__SolutionModel.objects(db)
        result = await obj.get(id=app__solution_id)
        if result:
            return result
        else:
            raise FileNotFoundError
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail={
                "field_name": "{app__solution_id}",
                "message": f"<{app__solution_id}> record not found in  apps__solutions"
            })
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, "could not fetch record <{app__solution_id}>")

get.__doc__ = f" Get a specific app__solution by its id".expandtabs()


# query apps__solutions
@router.post('/q', tags=['apps__solutions'], status_code=HTTP_200_OK, summary="Query apps__solutions: Projection, Limit/skips, Sorting, Filters, Joins, Aggregates, Count, Group")
async def query(q: QuerySchema, db: Session = Depends(get_sync_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-apps__solutions-list', 'zekoder-zestudio-apps__solutions-get'])
    
    try:
        size = q.limit if q.limit else 20
        page = int(q.skip)/size if q.skip else 1
        jq = JSONQ(db, App__SolutionModel)
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



# create app__solution
@router.post('/', tags=['apps__solutions'], status_code=HTTP_201_CREATED, summary="Create new app__solution", response_model=ReadApp__Solution)
async def create(request: Request, app__solution: CreateApp__Solution, db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-apps__solutions-create']) 
    
    try:
        new_data = app__solution.dict()
        kwargs = {
            "model_data": new_data,
            "signal_data": {
                "jwt": token.credentials,
                "new_data": new_data,
                "old_data": {},
                "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
            }
        }
        obj = await App__SolutionModel.objects(db)
        new_app__solution = await obj.create(**kwargs)
        return new_app__solution
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.args[-1])
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, f"creation of new app  solution failed")

create.__doc__ = f" Create a new app__solution".expandtabs()


# create multiple apps__solutions
@router.post('/add-apps__solutions', tags=['apps__solutions'], status_code=HTTP_201_CREATED, summary="Create multiple apps__solutions", response_model=List[ReadApp__Solution])
async def create_multiple_apps__solutions(request: Request, apps__solutions: List[CreateApp__Solution], db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-apps__solutions-create']) 
    
    new_items, errors_info = [], []
    try:
        for app__solution_index, app__solution in enumerate(apps__solutions):
            try:
                new_data = app__solution.dict()
                kwargs = {
                    "model_data": new_data,
                    "signal_data": {
                        "jwt": token.credentials,
                        "new_data": new_data,
                        "old_data": {},
                        "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
                    }
                }
                obj = await App__SolutionModel.objects(db)
                new_apps__solutions = await obj.create(only_add=True, **kwargs)
                new_items.append(new_apps__solutions)
            except HTTPException as e:
                errors_info.append({"index": app__solution_index, "errors": e.detail})

        return new_items
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.args[-1])
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, f"creation of new apps  solutions failed")

create.__doc__ = f" Create multiple new apps__solutions".expandtabs()


# upsert multiple apps__solutions
@router.post('/upsert-multiple-apps__solutions', tags=['apps__solutions'], status_code=HTTP_201_CREATED, summary="Upsert multiple apps__solutions", response_model=List[ReadApp__Solution])
async def upsert_multiple_apps__solutions(request: Request, apps__solutions: List[UpsertApp__Solution], db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-apps__solutions-create'])
    new_items, errors_info = [], []
    try:
        for app__solution_index, app__solution in enumerate(apps__solutions):
            try:
                new_data = app__solution.dict()
                kwargs = {
                    "model_data": new_data,
                    "signal_data": {
                        "jwt": token.credentials,
                        "new_data": new_data,
                        "old_data": {},
                        "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
                    }
                }
                obj = await App__SolutionModel.objects(db)
                old_data = await obj.get(id=new_data['id'])
                if old_data:
                    kwargs['signal_data']['old_data'] = dict(old_data.__dict__) if old_data else {}
                    obj = await App__SolutionModel.objects(db)
                    updated_apps__solutions = await obj.update(obj_id=new_data['id'], **kwargs)
                    new_items.append(updated_apps__solutions)
                else:
                    obj = await App__SolutionModel.objects(db)
                    new_apps__solutions = await obj.create(only_add=True, **kwargs)
                    new_items.append(new_apps__solutions)
            except HTTPException as e:
                errors_info.append({"index": app__solution_index, "errors": e.detail})

        return new_items
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.args[-1])
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, f"upsert multiple apps  solutions failed")

upsert_multiple_apps__solutions.__doc__ = f" upsert multiple apps__solutions".expandtabs()


# update app__solution
@router.put('/app__solution_id', tags=['apps__solutions'], status_code=HTTP_201_CREATED, summary="Update app__solution with ID")
async def update(request: Request, app__solution_id: Union[str, int], app__solution: UpdateApp__Solution, db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-apps__solutions-update'])
    try:
        obj = await App__SolutionModel.objects(db)
        old_data = await obj.get(id=app__solution_id)
        new_data = app__solution.dict(exclude_unset=True)
        kwargs = {
            "model_data": new_data,
            "signal_data": {
                "jwt": token.credentials,
                "new_data": new_data,
                "old_data": dict(old_data.__dict__) if old_data else {},
                "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
            }
        }
        obj = await App__SolutionModel.objects(db)
        result = await obj.update(obj_id=app__solution_id, **kwargs)
        return result
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.args[-1])
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, "failed updating session with id <{session_id}>")

update.__doc__ = f" Update a app__solution by its id and payload".expandtabs()


# delete app__solution
@router.delete('/app__solution_id', tags=['apps__solutions'], status_code=HTTP_204_NO_CONTENT, summary="Delete app__solution with ID", response_class=Response)
async def delete(request: Request, app__solution_id: Union[str, int], db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-apps__solutions-delete'])
    try:
        obj = await App__SolutionModel.objects(db)
        old_data = await obj.get(id=app__solution_id)
        kwargs = {
            "model_data": {},
            "signal_data": {
                "jwt": token.credentials,
                "new_data": {},
                "old_data": dict(old_data.__dict__) if old_data else {},
                "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
            }
        }
        obj = await App__SolutionModel.objects(db)
        await obj.delete(obj_id=app__solution_id, **kwargs)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail={
                "field_name": "{app__solution_id}",
                "message": f"<{app__solution_id}> record not found in  apps__solutions"
            })
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, "failed updating session with id <{session_id}>")

delete.__doc__ = f" Delete a app__solution by its id".expandtabs()


# delete multiple apps__solutions
@router.delete('/delete-apps__solutions', tags=['apps__solutions'], status_code=HTTP_204_NO_CONTENT, summary="Delete multiple apps__solutions with IDs", response_class=Response)
async def delete_multiple_apps__solutions(request: Request, apps__solutions_id: List[str] = QueryParam(), db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-apps__solutions-delete'])
    kwargs = {
        "model_data": {},
        "signal_data": {
            "jwt": token.credentials,
            "new_data": {},
            "old_data": {},
            "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
        }
    }
    obj = await App__SolutionModel.objects(db)
    await obj.delete_multiple(obj_ids=apps__solutions_id, **kwargs)

delete.__doc__ = f" Delete multiple apps__solutions by list of ids".expandtabs()

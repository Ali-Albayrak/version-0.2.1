from typing import Union, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response, Query as QueryParam
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from starlette.status import HTTP_204_NO_CONTENT, HTTP_200_OK, HTTP_201_CREATED

from business.solution_versions_schema import *
from business.solution_versions_model import Solution_VersionModel

from core.depends import CommonDependencies, get_async_db, get_sync_db, Protect, zeauth_url
from core.logger import log
from core.query import *
from actions import solution_version_create, solution_version_update
from business.solution_versions_model import Solution_VersionModel


router = APIRouter()


  
# list solution_versions
@router.get('/', tags=['solution_versions'], status_code=HTTP_200_OK, summary="List solution_versions", response_model=ReadSolution_Versions)
async def list(request: Request, token: str = Depends(Protect), db: AsyncSession = Depends(get_async_db), commons: CommonDependencies = Depends(CommonDependencies)):
    token.auth(['zekoder-zestudio-solution_versions-list', 'zekoder-zestudio-solution_versions-get'])
    try:
        obj = await Solution_VersionModel.objects(db)
        result = await obj.all(offset=commons.offset, limit=commons.size)
        return {
            'data': result,
            'page_size': commons.size,
            'next_page': int(commons.page) + 1
        }
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, "could not fetch list of solution_version")

list.__doc__ = f" List solution_versions".expandtabs()


# get solution_version
@router.get('/solution_version_id', tags=['solution_versions'], status_code=HTTP_200_OK, summary="Get solution_version with ID", response_model=ReadSolution_Version)
async def get(request: Request, solution_version_id: str, db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-solution_versions-list', 'zekoder-zestudio-solution_versions-get'])
    try:
        obj = await Solution_VersionModel.objects(db)
        result = await obj.get(id=solution_version_id)
        if result:
            return result
        else:
            raise FileNotFoundError
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail={
                "field_name": "{solution_version_id}",
                "message": f"<{solution_version_id}> record not found in  solution_versions"
            })
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, "could not fetch record <{solution_version_id}>")

get.__doc__ = f" Get a specific solution_version by its id".expandtabs()


# query solution_versions
@router.post('/q', tags=['solution_versions'], status_code=HTTP_200_OK, summary="Query solution_versions: Projection, Limit/skips, Sorting, Filters, Joins, Aggregates, Count, Group")
async def query(q: QuerySchema, db: Session = Depends(get_sync_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-solution_versions-list', 'zekoder-zestudio-solution_versions-get'])
    
    try:
        size = q.limit if q.limit else 20
        page = int(q.skip)/size if q.skip else 1
        jq = JSONQ(db, Solution_VersionModel)
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



# create solution_version
@router.post('/', tags=['solution_versions'], status_code=HTTP_201_CREATED, summary="Create new solution_version", response_model=ReadSolution_Version)
async def create(request: Request, solution_version: CreateSolution_Version, db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-solution_versions-create']) 
    
    try:
        await Solution_VersionModel.validate_unique_version_solution(db, solution_version.version, solution_version.solution)
        new_data = solution_version.dict()
        kwargs = {
            "model_data": new_data,
            "signal_data": {
                "jwt": token.credentials,
                "new_data": new_data,
                "old_data": {},
                "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
            }
        }
        obj = await Solution_VersionModel.objects(db)
        new_solution_version = await obj.create(**kwargs)
        return new_solution_version
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.args[-1])
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, f"creation of new solution version failed")

create.__doc__ = f" Create a new solution_version".expandtabs()


# create multiple solution_versions
@router.post('/add-solution_versions', tags=['solution_versions'], status_code=HTTP_201_CREATED, summary="Create multiple solution_versions", response_model=List[ReadSolution_Version])
async def create_multiple_solution_versions(request: Request, solution_versions: List[CreateSolution_Version], db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-solution_versions-create']) 
    
    new_items, errors_info = [], []
    try:
        for solution_version_index, solution_version in enumerate(solution_versions):
            try:
                await Solution_VersionModel.validate_unique_version_solution(db, solution_version.version, solution_version.solution)
                new_data = solution_version.dict()
                kwargs = {
                    "model_data": new_data,
                    "signal_data": {
                        "jwt": token.credentials,
                        "new_data": new_data,
                        "old_data": {},
                        "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
                    }
                }
                obj = await Solution_VersionModel.objects(db)
                new_solution_versions = await obj.create(only_add=True, **kwargs)
                new_items.append(new_solution_versions)
            except HTTPException as e:
                errors_info.append({"index": solution_version_index, "errors": e.detail})

        if errors_info:
            return JSONResponse(errors_info, 422)
        return new_items
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.args[-1])
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, f"creation of new solution versions failed")

create.__doc__ = f" Create multiple new solution_versions".expandtabs()


# upsert multiple solution_versions
@router.post('/upsert-multiple-solution_versions', tags=['solution_versions'], status_code=HTTP_201_CREATED, summary="Upsert multiple solution_versions", response_model=List[ReadSolution_Version])
async def upsert_multiple_solution_versions(request: Request, solution_versions: List[UpsertSolution_Version], db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-solution_versions-create'])
    new_items, errors_info = [], []
    try:
        for solution_version_index, solution_version in enumerate(solution_versions):
            try:
                await Solution_VersionModel.validate_unique_version_solution(db, solution_version.version, solution_version.solution)
                new_data = solution_version.dict()
                kwargs = {
                    "model_data": new_data,
                    "signal_data": {
                        "jwt": token.credentials,
                        "new_data": new_data,
                        "old_data": {},
                        "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
                    }
                }
                obj = await Solution_VersionModel.objects(db)
                old_data = await obj.get(id=new_data['id'])
                if old_data:
                    kwargs['signal_data']['old_data'] = dict(old_data.__dict__) if old_data else {}
                    obj = await Solution_VersionModel.objects(db)
                    updated_solution_versions = await obj.update(obj_id=new_data['id'], **kwargs)
                    new_items.append(updated_solution_versions)
                else:
                    obj = await Solution_VersionModel.objects(db)
                    new_solution_versions = await obj.create(only_add=True, **kwargs)
                    new_items.append(new_solution_versions)
            except HTTPException as e:
                errors_info.append({"index": solution_version_index, "errors": e.detail})

        if errors_info:
            return JSONResponse(errors_info, 422)
        return new_items
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.args[-1])
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, f"upsert multiple solution versions failed")

upsert_multiple_solution_versions.__doc__ = f" upsert multiple solution_versions".expandtabs()


# update solution_version
@router.put('/solution_version_id', tags=['solution_versions'], status_code=HTTP_201_CREATED, summary="Update solution_version with ID")
async def update(request: Request, solution_version_id: Union[str, int], solution_version: UpdateSolution_Version, db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-solution_versions-update'])
    try:
        await Solution_VersionModel.validate_unique_version_solution(db, solution_version.version, solution_version.solution, solution_version_id)
        obj = await Solution_VersionModel.objects(db)
        old_data = await obj.get(id=solution_version_id)
        new_data = solution_version.dict(exclude_unset=True)
        kwargs = {
            "model_data": new_data,
            "signal_data": {
                "jwt": token.credentials,
                "new_data": new_data,
                "old_data": dict(old_data.__dict__) if old_data else {},
                "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
            }
        }
        obj = await Solution_VersionModel.objects(db)
        result = await obj.update(obj_id=solution_version_id, **kwargs)
        return result
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.args[-1])
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, "failed updating session with id <{session_id}>")

update.__doc__ = f" Update a solution_version by its id and payload".expandtabs()


# delete solution_version
@router.delete('/solution_version_id', tags=['solution_versions'], status_code=HTTP_204_NO_CONTENT, summary="Delete solution_version with ID", response_class=Response)
async def delete(request: Request, solution_version_id: Union[str, int], db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-solution_versions-delete'])
    try:
        obj = await Solution_VersionModel.objects(db)
        old_data = await obj.get(id=solution_version_id)
        kwargs = {
            "model_data": {},
            "signal_data": {
                "jwt": token.credentials,
                "new_data": {},
                "old_data": dict(old_data.__dict__) if old_data else {},
                "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
            }
        }
        obj = await Solution_VersionModel.objects(db)
        await obj.delete(obj_id=solution_version_id, **kwargs)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail={
                "field_name": "{solution_version_id}",
                "message": f"<{solution_version_id}> record not found in  solution_versions"
            })
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, "failed updating session with id <{session_id}>")

delete.__doc__ = f" Delete a solution_version by its id".expandtabs()


# delete multiple solution_versions
@router.delete('/delete-solution_versions', tags=['solution_versions'], status_code=HTTP_204_NO_CONTENT, summary="Delete multiple solution_versions with IDs", response_class=Response)
async def delete_multiple_solution_versions(request: Request, solution_versions_id: List[str] = QueryParam(), db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-solution_versions-delete'])
    kwargs = {
        "model_data": {},
        "signal_data": {
            "jwt": token.credentials,
            "new_data": {},
            "old_data": {},
            "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
        }
    }
    obj = await Solution_VersionModel.objects(db)
    await obj.delete_multiple(obj_ids=solution_versions_id, **kwargs)

delete.__doc__ = f" Delete multiple solution_versions by list of ids".expandtabs()

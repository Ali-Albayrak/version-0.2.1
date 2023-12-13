from typing import Union, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response, Query as QueryParam
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from starlette.status import HTTP_204_NO_CONTENT, HTTP_200_OK, HTTP_201_CREATED

from business.solutions_schema import *
from business.solutions_model import SolutionModel

from core.depends import CommonDependencies, get_async_db, get_sync_db, Protect, zeauth_url
from core.logger import log
from core.query import *

from business.solutions_model import SolutionModel


router = APIRouter()


  
# list solutions
@router.get('/', tags=['solutions'], status_code=HTTP_200_OK, summary="List solutions", response_model=ReadSolutions)
async def list(request: Request, token: str = Depends(Protect), db: AsyncSession = Depends(get_async_db), commons: CommonDependencies = Depends(CommonDependencies)):
    token.auth(['zekoder-zestudio-solutions-list', 'zekoder-zestudio-solutions-get'])
    try:
        obj = await SolutionModel.objects(db)
        result = await obj.all(offset=commons.offset, limit=commons.size)
        return {
            'data': result,
            'page_size': commons.size,
            'next_page': int(commons.page) + 1
        }
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, "could not fetch list of solution")

list.__doc__ = f" List solutions".expandtabs()


# get solution
@router.get('/solution_id', tags=['solutions'], status_code=HTTP_200_OK, summary="Get solution with ID", response_model=ReadSolution)
async def get(request: Request, solution_id: str, db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-solutions-list', 'zekoder-zestudio-solutions-get'])
    try:
        obj = await SolutionModel.objects(db)
        result = await obj.get(id=solution_id)
        if result:
            return result
        else:
            raise FileNotFoundError
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail={
                "field_name": "{solution_id}",
                "message": f"<{solution_id}> record not found in  solutions"
            })
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, "could not fetch record <{solution_id}>")

get.__doc__ = f" Get a specific solution by its id".expandtabs()


# query solutions
@router.post('/q', tags=['solutions'], status_code=HTTP_200_OK, summary="Query solutions: Projection, Limit/skips, Sorting, Filters, Joins, Aggregates, Count, Group")
async def query(q: QuerySchema, db: Session = Depends(get_sync_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-solutions-list', 'zekoder-zestudio-solutions-get'])
    
    try:
        size = q.limit if q.limit else 20
        page = int(q.skip)/size if q.skip else 1
        jq = JSONQ(db, SolutionModel)
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



# create solution
@router.post('/', tags=['solutions'], status_code=HTTP_201_CREATED, summary="Create new solution", response_model=ReadSolution)
async def create(request: Request, solution: CreateSolution, db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-solutions-create']) 
    
    try:
        await SolutionModel.validate_unique_short_name(db, solution.short_name)
        new_data = solution.dict()
        kwargs = {
            "model_data": new_data,
            "signal_data": {
                "jwt": token.credentials,
                "new_data": new_data,
                "old_data": {},
                "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
            }
        }
        obj = await SolutionModel.objects(db)
        new_solution = await obj.create(**kwargs)
        return new_solution
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.args[-1])
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, f"creation of new solution failed")

create.__doc__ = f" Create a new solution".expandtabs()


# create multiple solutions
@router.post('/add-solutions', tags=['solutions'], status_code=HTTP_201_CREATED, summary="Create multiple solutions", response_model=List[ReadSolution])
async def create_multiple_solutions(request: Request, solutions: List[CreateSolution], db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-solutions-create']) 
    
    new_items, errors_info = [], []
    try:
        for solution_index, solution in enumerate(solutions):
            try:
                await SolutionModel.validate_unique_short_name(db, solution.short_name)
                new_data = solution.dict()
                kwargs = {
                    "model_data": new_data,
                    "signal_data": {
                        "jwt": token.credentials,
                        "new_data": new_data,
                        "old_data": {},
                        "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
                    }
                }
                obj = await SolutionModel.objects(db)
                new_solutions = await obj.create(only_add=True, **kwargs)
                new_items.append(new_solutions)
            except HTTPException as e:
                errors_info.append({"index": solution_index, "errors": e.detail})

        if errors_info:
            return JSONResponse(errors_info, 422)
        return new_items
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.args[-1])
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, f"creation of new solutions failed")

create.__doc__ = f" Create multiple new solutions".expandtabs()


# upsert multiple solutions
@router.post('/upsert-multiple-solutions', tags=['solutions'], status_code=HTTP_201_CREATED, summary="Upsert multiple solutions", response_model=List[ReadSolution])
async def upsert_multiple_solutions(request: Request, solutions: List[UpsertSolution], db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-solutions-create'])
    new_items, errors_info = [], []
    try:
        for solution_index, solution in enumerate(solutions):
            try:
                await SolutionModel.validate_unique_short_name(db, solution.short_name)
                new_data = solution.dict()
                kwargs = {
                    "model_data": new_data,
                    "signal_data": {
                        "jwt": token.credentials,
                        "new_data": new_data,
                        "old_data": {},
                        "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
                    }
                }
                obj = await SolutionModel.objects(db)
                old_data = await obj.get(id=new_data['id'])
                if old_data:
                    kwargs['signal_data']['old_data'] = dict(old_data.__dict__) if old_data else {}
                    obj = await SolutionModel.objects(db)
                    updated_solutions = await obj.update(obj_id=new_data['id'], **kwargs)
                    new_items.append(updated_solutions)
                else:
                    obj = await SolutionModel.objects(db)
                    new_solutions = await obj.create(only_add=True, **kwargs)
                    new_items.append(new_solutions)
            except HTTPException as e:
                errors_info.append({"index": solution_index, "errors": e.detail})

        if errors_info:
            return JSONResponse(errors_info, 422)
        return new_items
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.args[-1])
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, f"upsert multiple solutions failed")

upsert_multiple_solutions.__doc__ = f" upsert multiple solutions".expandtabs()


# update solution
@router.put('/solution_id', tags=['solutions'], status_code=HTTP_201_CREATED, summary="Update solution with ID")
async def update(request: Request, solution_id: Union[str, int], solution: UpdateSolution, db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-solutions-update'])
    try:
        await SolutionModel.validate_unique_short_name(db, solution.short_name, solution_id)
        obj = await SolutionModel.objects(db)
        old_data = await obj.get(id=solution_id)
        new_data = solution.dict(exclude_unset=True)
        kwargs = {
            "model_data": new_data,
            "signal_data": {
                "jwt": token.credentials,
                "new_data": new_data,
                "old_data": dict(old_data.__dict__) if old_data else {},
                "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
            }
        }
        obj = await SolutionModel.objects(db)
        result = await obj.update(obj_id=solution_id, **kwargs)
        return result
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.args[-1])
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, "failed updating session with id <{session_id}>")

update.__doc__ = f" Update a solution by its id and payload".expandtabs()


# delete solution
@router.delete('/solution_id', tags=['solutions'], status_code=HTTP_204_NO_CONTENT, summary="Delete solution with ID", response_class=Response)
async def delete(request: Request, solution_id: Union[str, int], db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-solutions-delete'])
    try:
        obj = await SolutionModel.objects(db)
        old_data = await obj.get(id=solution_id)
        kwargs = {
            "model_data": {},
            "signal_data": {
                "jwt": token.credentials,
                "new_data": {},
                "old_data": dict(old_data.__dict__) if old_data else {},
                "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
            }
        }
        obj = await SolutionModel.objects(db)
        await obj.delete(obj_id=solution_id, **kwargs)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail={
                "field_name": "{solution_id}",
                "message": f"<{solution_id}> record not found in  solutions"
            })
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, "failed updating session with id <{session_id}>")

delete.__doc__ = f" Delete a solution by its id".expandtabs()


# delete multiple solutions
@router.delete('/delete-solutions', tags=['solutions'], status_code=HTTP_204_NO_CONTENT, summary="Delete multiple solutions with IDs", response_class=Response)
async def delete_multiple_solutions(request: Request, solutions_id: List[str] = QueryParam(), db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-solutions-delete'])
    kwargs = {
        "model_data": {},
        "signal_data": {
            "jwt": token.credentials,
            "new_data": {},
            "old_data": {},
            "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
        }
    }
    obj = await SolutionModel.objects(db)
    await obj.delete_multiple(obj_ids=solutions_id, **kwargs)

delete.__doc__ = f" Delete multiple solutions by list of ids".expandtabs()

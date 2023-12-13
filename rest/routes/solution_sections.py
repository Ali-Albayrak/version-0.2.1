from typing import Union, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response, Query as QueryParam
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from starlette.status import HTTP_204_NO_CONTENT, HTTP_200_OK, HTTP_201_CREATED

from business.solution_sections_schema import *
from business.solution_sections_model import Solution_SectionModel

from core.depends import CommonDependencies, get_async_db, get_sync_db, Protect, zeauth_url
from core.logger import log
from core.query import *

from business.solution_sections_model import Solution_SectionModel


router = APIRouter()


  
# list solution_sections
@router.get('/', tags=['solution_sections'], status_code=HTTP_200_OK, summary="List solution_sections", response_model=ReadSolution_Sections)
async def list(request: Request, token: str = Depends(Protect), db: AsyncSession = Depends(get_async_db), commons: CommonDependencies = Depends(CommonDependencies)):
    token.auth(['zekoder-zestudio-solution_sections-list', 'zekoder-zestudio-solution_sections-get'])
    try:
        obj = await Solution_SectionModel.objects(db)
        result = await obj.all(offset=commons.offset, limit=commons.size)
        return {
            'data': result,
            'page_size': commons.size,
            'next_page': int(commons.page) + 1
        }
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, "could not fetch list of solution_section")

list.__doc__ = f" List solution_sections".expandtabs()


# get solution_section
@router.get('/solution_section_id', tags=['solution_sections'], status_code=HTTP_200_OK, summary="Get solution_section with ID", response_model=ReadSolution_Section)
async def get(request: Request, solution_section_id: str, db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-solution_sections-list', 'zekoder-zestudio-solution_sections-get'])
    try:
        obj = await Solution_SectionModel.objects(db)
        result = await obj.get(id=solution_section_id)
        if result:
            return result
        else:
            raise FileNotFoundError
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail={
                "field_name": "{solution_section_id}",
                "message": f"<{solution_section_id}> record not found in  solution_sections"
            })
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, "could not fetch record <{solution_section_id}>")

get.__doc__ = f" Get a specific solution_section by its id".expandtabs()


# query solution_sections
@router.post('/q', tags=['solution_sections'], status_code=HTTP_200_OK, summary="Query solution_sections: Projection, Limit/skips, Sorting, Filters, Joins, Aggregates, Count, Group")
async def query(q: QuerySchema, db: Session = Depends(get_sync_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-solution_sections-list', 'zekoder-zestudio-solution_sections-get'])
    
    try:
        size = q.limit if q.limit else 20
        page = int(q.skip)/size if q.skip else 1
        jq = JSONQ(db, Solution_SectionModel)
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



# create solution_section
@router.post('/', tags=['solution_sections'], status_code=HTTP_201_CREATED, summary="Create new solution_section", response_model=ReadSolution_Section)
async def create(request: Request, solution_section: CreateSolution_Section, db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-solution_sections-create']) 
    
    try:
        await Solution_SectionModel.validate_unique_type_solution(db, solution_section.type, solution_section.solution)
        new_data = solution_section.dict()
        kwargs = {
            "model_data": new_data,
            "signal_data": {
                "jwt": token.credentials,
                "new_data": new_data,
                "old_data": {},
                "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
            }
        }
        obj = await Solution_SectionModel.objects(db)
        new_solution_section = await obj.create(**kwargs)
        return new_solution_section
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.args[-1])
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, f"creation of new solution section failed")

create.__doc__ = f" Create a new solution_section".expandtabs()


# create multiple solution_sections
@router.post('/add-solution_sections', tags=['solution_sections'], status_code=HTTP_201_CREATED, summary="Create multiple solution_sections", response_model=List[ReadSolution_Section])
async def create_multiple_solution_sections(request: Request, solution_sections: List[CreateSolution_Section], db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-solution_sections-create']) 
    
    new_items, errors_info = [], []
    try:
        for solution_section_index, solution_section in enumerate(solution_sections):
            try:
                await Solution_SectionModel.validate_unique_type_solution(db, solution_section.type, solution_section.solution)
                new_data = solution_section.dict()
                kwargs = {
                    "model_data": new_data,
                    "signal_data": {
                        "jwt": token.credentials,
                        "new_data": new_data,
                        "old_data": {},
                        "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
                    }
                }
                obj = await Solution_SectionModel.objects(db)
                new_solution_sections = await obj.create(only_add=True, **kwargs)
                new_items.append(new_solution_sections)
            except HTTPException as e:
                errors_info.append({"index": solution_section_index, "errors": e.detail})

        if errors_info:
            return JSONResponse(errors_info, 422)
        return new_items
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.args[-1])
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, f"creation of new solution sections failed")

create.__doc__ = f" Create multiple new solution_sections".expandtabs()


# upsert multiple solution_sections
@router.post('/upsert-multiple-solution_sections', tags=['solution_sections'], status_code=HTTP_201_CREATED, summary="Upsert multiple solution_sections", response_model=List[ReadSolution_Section])
async def upsert_multiple_solution_sections(request: Request, solution_sections: List[UpsertSolution_Section], db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-solution_sections-create'])
    new_items, errors_info = [], []
    try:
        for solution_section_index, solution_section in enumerate(solution_sections):
            try:
                await Solution_SectionModel.validate_unique_type_solution(db, solution_section.type, solution_section.solution)
                new_data = solution_section.dict()
                kwargs = {
                    "model_data": new_data,
                    "signal_data": {
                        "jwt": token.credentials,
                        "new_data": new_data,
                        "old_data": {},
                        "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
                    }
                }
                obj = await Solution_SectionModel.objects(db)
                old_data = await obj.get(id=new_data['id'])
                if old_data:
                    kwargs['signal_data']['old_data'] = dict(old_data.__dict__) if old_data else {}
                    obj = await Solution_SectionModel.objects(db)
                    updated_solution_sections = await obj.update(obj_id=new_data['id'], **kwargs)
                    new_items.append(updated_solution_sections)
                else:
                    obj = await Solution_SectionModel.objects(db)
                    new_solution_sections = await obj.create(only_add=True, **kwargs)
                    new_items.append(new_solution_sections)
            except HTTPException as e:
                errors_info.append({"index": solution_section_index, "errors": e.detail})

        if errors_info:
            return JSONResponse(errors_info, 422)
        return new_items
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.args[-1])
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, f"upsert multiple solution sections failed")

upsert_multiple_solution_sections.__doc__ = f" upsert multiple solution_sections".expandtabs()


# update solution_section
@router.put('/solution_section_id', tags=['solution_sections'], status_code=HTTP_201_CREATED, summary="Update solution_section with ID")
async def update(request: Request, solution_section_id: Union[str, int], solution_section: UpdateSolution_Section, db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-solution_sections-update'])
    try:
        await Solution_SectionModel.validate_unique_type_solution(db, solution_section.type, solution_section.solution, solution_section_id)
        obj = await Solution_SectionModel.objects(db)
        old_data = await obj.get(id=solution_section_id)
        new_data = solution_section.dict(exclude_unset=True)
        kwargs = {
            "model_data": new_data,
            "signal_data": {
                "jwt": token.credentials,
                "new_data": new_data,
                "old_data": dict(old_data.__dict__) if old_data else {},
                "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
            }
        }
        obj = await Solution_SectionModel.objects(db)
        result = await obj.update(obj_id=solution_section_id, **kwargs)
        return result
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.args[-1])
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, "failed updating session with id <{session_id}>")

update.__doc__ = f" Update a solution_section by its id and payload".expandtabs()


# delete solution_section
@router.delete('/solution_section_id', tags=['solution_sections'], status_code=HTTP_204_NO_CONTENT, summary="Delete solution_section with ID", response_class=Response)
async def delete(request: Request, solution_section_id: Union[str, int], db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-solution_sections-delete'])
    try:
        obj = await Solution_SectionModel.objects(db)
        old_data = await obj.get(id=solution_section_id)
        kwargs = {
            "model_data": {},
            "signal_data": {
                "jwt": token.credentials,
                "new_data": {},
                "old_data": dict(old_data.__dict__) if old_data else {},
                "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
            }
        }
        obj = await Solution_SectionModel.objects(db)
        await obj.delete(obj_id=solution_section_id, **kwargs)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail={
                "field_name": "{solution_section_id}",
                "message": f"<{solution_section_id}> record not found in  solution_sections"
            })
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, "failed updating session with id <{session_id}>")

delete.__doc__ = f" Delete a solution_section by its id".expandtabs()


# delete multiple solution_sections
@router.delete('/delete-solution_sections', tags=['solution_sections'], status_code=HTTP_204_NO_CONTENT, summary="Delete multiple solution_sections with IDs", response_class=Response)
async def delete_multiple_solution_sections(request: Request, solution_sections_id: List[str] = QueryParam(), db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-solution_sections-delete'])
    kwargs = {
        "model_data": {},
        "signal_data": {
            "jwt": token.credentials,
            "new_data": {},
            "old_data": {},
            "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
        }
    }
    obj = await Solution_SectionModel.objects(db)
    await obj.delete_multiple(obj_ids=solution_sections_id, **kwargs)

delete.__doc__ = f" Delete multiple solution_sections by list of ids".expandtabs()

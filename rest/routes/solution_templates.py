from typing import Union, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response, Query as QueryParam
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from starlette.status import HTTP_204_NO_CONTENT, HTTP_200_OK, HTTP_201_CREATED

from business.solution_templates_schema import *
from business.solution_templates_model import Solution_TemplateModel

from core.depends import CommonDependencies, get_async_db, get_sync_db, Protect, zeauth_url
from core.logger import log
from core.query import *

from business.solution_templates_model import Solution_TemplateModel


router = APIRouter()


  
# list solution_templates
@router.get('/', tags=['solution_templates'], status_code=HTTP_200_OK, summary="List solution_templates", response_model=ReadSolution_Templates)
async def list(request: Request, token: str = Depends(Protect), db: AsyncSession = Depends(get_async_db), commons: CommonDependencies = Depends(CommonDependencies)):
    token.auth(['zekoder-zestudio-solution_templates-list', 'zekoder-zestudio-solution_templates-get'])
    try:
        obj = await Solution_TemplateModel.objects(db)
        result = await obj.all(offset=commons.offset, limit=commons.size)
        return {
            'data': result,
            'page_size': commons.size,
            'next_page': int(commons.page) + 1
        }
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, "could not fetch list of solution_template")

list.__doc__ = f" List solution_templates".expandtabs()


# get solution_template
@router.get('/solution_template_id', tags=['solution_templates'], status_code=HTTP_200_OK, summary="Get solution_template with ID", response_model=ReadSolution_Template)
async def get(request: Request, solution_template_id: str, db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-solution_templates-list', 'zekoder-zestudio-solution_templates-get'])
    try:
        obj = await Solution_TemplateModel.objects(db)
        result = await obj.get(id=solution_template_id)
        if result:
            return result
        else:
            raise FileNotFoundError
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail={
                "field_name": "{solution_template_id}",
                "message": f"<{solution_template_id}> record not found in  solution_templates"
            })
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, "could not fetch record <{solution_template_id}>")

get.__doc__ = f" Get a specific solution_template by its id".expandtabs()


# query solution_templates
@router.post('/q', tags=['solution_templates'], status_code=HTTP_200_OK, summary="Query solution_templates: Projection, Limit/skips, Sorting, Filters, Joins, Aggregates, Count, Group")
async def query(q: QuerySchema, db: Session = Depends(get_sync_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-solution_templates-list', 'zekoder-zestudio-solution_templates-get'])
    
    try:
        size = q.limit if q.limit else 20
        page = int(q.skip)/size if q.skip else 1
        jq = JSONQ(db, Solution_TemplateModel)
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



# create solution_template
@router.post('/', tags=['solution_templates'], status_code=HTTP_201_CREATED, summary="Create new solution_template", response_model=ReadSolution_Template)
async def create(request: Request, solution_template: CreateSolution_Template, db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-solution_templates-create']) 
    
    try:
        new_data = solution_template.dict()
        kwargs = {
            "model_data": new_data,
            "signal_data": {
                "jwt": token.credentials,
                "new_data": new_data,
                "old_data": {},
                "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
            }
        }
        obj = await Solution_TemplateModel.objects(db)
        new_solution_template = await obj.create(**kwargs)
        return new_solution_template
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.args[-1])
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, f"creation of new solution template failed")

create.__doc__ = f" Create a new solution_template".expandtabs()


# create multiple solution_templates
@router.post('/add-solution_templates', tags=['solution_templates'], status_code=HTTP_201_CREATED, summary="Create multiple solution_templates", response_model=List[ReadSolution_Template])
async def create_multiple_solution_templates(request: Request, solution_templates: List[CreateSolution_Template], db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-solution_templates-create']) 
    
    new_items, errors_info = [], []
    try:
        for solution_template_index, solution_template in enumerate(solution_templates):
            try:
                new_data = solution_template.dict()
                kwargs = {
                    "model_data": new_data,
                    "signal_data": {
                        "jwt": token.credentials,
                        "new_data": new_data,
                        "old_data": {},
                        "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
                    }
                }
                obj = await Solution_TemplateModel.objects(db)
                new_solution_templates = await obj.create(only_add=True, **kwargs)
                new_items.append(new_solution_templates)
            except HTTPException as e:
                errors_info.append({"index": solution_template_index, "errors": e.detail})

        return new_items
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.args[-1])
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, f"creation of new solution templates failed")

create.__doc__ = f" Create multiple new solution_templates".expandtabs()


# upsert multiple solution_templates
@router.post('/upsert-multiple-solution_templates', tags=['solution_templates'], status_code=HTTP_201_CREATED, summary="Upsert multiple solution_templates", response_model=List[ReadSolution_Template])
async def upsert_multiple_solution_templates(request: Request, solution_templates: List[UpsertSolution_Template], db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-solution_templates-create'])
    new_items, errors_info = [], []
    try:
        for solution_template_index, solution_template in enumerate(solution_templates):
            try:
                new_data = solution_template.dict()
                kwargs = {
                    "model_data": new_data,
                    "signal_data": {
                        "jwt": token.credentials,
                        "new_data": new_data,
                        "old_data": {},
                        "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
                    }
                }
                obj = await Solution_TemplateModel.objects(db)
                old_data = await obj.get(id=new_data['id'])
                if old_data:
                    kwargs['signal_data']['old_data'] = dict(old_data.__dict__) if old_data else {}
                    obj = await Solution_TemplateModel.objects(db)
                    updated_solution_templates = await obj.update(obj_id=new_data['id'], **kwargs)
                    new_items.append(updated_solution_templates)
                else:
                    obj = await Solution_TemplateModel.objects(db)
                    new_solution_templates = await obj.create(only_add=True, **kwargs)
                    new_items.append(new_solution_templates)
            except HTTPException as e:
                errors_info.append({"index": solution_template_index, "errors": e.detail})

        return new_items
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.args[-1])
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, f"upsert multiple solution templates failed")

upsert_multiple_solution_templates.__doc__ = f" upsert multiple solution_templates".expandtabs()


# update solution_template
@router.put('/solution_template_id', tags=['solution_templates'], status_code=HTTP_201_CREATED, summary="Update solution_template with ID")
async def update(request: Request, solution_template_id: Union[str, int], solution_template: UpdateSolution_Template, db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-solution_templates-update'])
    try:
        obj = await Solution_TemplateModel.objects(db)
        old_data = await obj.get(id=solution_template_id)
        new_data = solution_template.dict(exclude_unset=True)
        kwargs = {
            "model_data": new_data,
            "signal_data": {
                "jwt": token.credentials,
                "new_data": new_data,
                "old_data": dict(old_data.__dict__) if old_data else {},
                "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
            }
        }
        obj = await Solution_TemplateModel.objects(db)
        result = await obj.update(obj_id=solution_template_id, **kwargs)
        return result
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.args[-1])
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, "failed updating session with id <{session_id}>")

update.__doc__ = f" Update a solution_template by its id and payload".expandtabs()


# delete solution_template
@router.delete('/solution_template_id', tags=['solution_templates'], status_code=HTTP_204_NO_CONTENT, summary="Delete solution_template with ID", response_class=Response)
async def delete(request: Request, solution_template_id: Union[str, int], db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-solution_templates-delete'])
    try:
        obj = await Solution_TemplateModel.objects(db)
        old_data = await obj.get(id=solution_template_id)
        kwargs = {
            "model_data": {},
            "signal_data": {
                "jwt": token.credentials,
                "new_data": {},
                "old_data": dict(old_data.__dict__) if old_data else {},
                "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
            }
        }
        obj = await Solution_TemplateModel.objects(db)
        await obj.delete(obj_id=solution_template_id, **kwargs)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail={
                "field_name": "{solution_template_id}",
                "message": f"<{solution_template_id}> record not found in  solution_templates"
            })
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, "failed updating session with id <{session_id}>")

delete.__doc__ = f" Delete a solution_template by its id".expandtabs()


# delete multiple solution_templates
@router.delete('/delete-solution_templates', tags=['solution_templates'], status_code=HTTP_204_NO_CONTENT, summary="Delete multiple solution_templates with IDs", response_class=Response)
async def delete_multiple_solution_templates(request: Request, solution_templates_id: List[str] = QueryParam(), db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-solution_templates-delete'])
    kwargs = {
        "model_data": {},
        "signal_data": {
            "jwt": token.credentials,
            "new_data": {},
            "old_data": {},
            "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
        }
    }
    obj = await Solution_TemplateModel.objects(db)
    await obj.delete_multiple(obj_ids=solution_templates_id, **kwargs)

delete.__doc__ = f" Delete multiple solution_templates by list of ids".expandtabs()

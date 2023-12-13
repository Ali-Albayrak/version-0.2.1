from typing import Union, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response, Query as QueryParam
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from starlette.status import HTTP_204_NO_CONTENT, HTTP_200_OK, HTTP_201_CREATED

from business.sections_schema import *
from business.sections_model import SectionModel

from core.depends import CommonDependencies, get_async_db, get_sync_db, Protect, zeauth_url
from core.logger import log
from core.query import *

from business.sections_model import SectionModel


router = APIRouter()


  
# list sections
@router.get('/', tags=['sections'], status_code=HTTP_200_OK, summary="List sections", response_model=ReadSections)
async def list(request: Request, token: str = Depends(Protect), db: AsyncSession = Depends(get_async_db), commons: CommonDependencies = Depends(CommonDependencies)):
    token.auth(['zekoder-zestudio-sections-list', 'zekoder-zestudio-sections-get'])
    try:
        obj = await SectionModel.objects(db)
        result = await obj.all(offset=commons.offset, limit=commons.size)
        return {
            'data': result,
            'page_size': commons.size,
            'next_page': int(commons.page) + 1
        }
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, "could not fetch list of section")

list.__doc__ = f" List sections".expandtabs()


# get section
@router.get('/section_id', tags=['sections'], status_code=HTTP_200_OK, summary="Get section with ID", response_model=ReadSection)
async def get(request: Request, section_id: str, db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-sections-list', 'zekoder-zestudio-sections-get'])
    try:
        obj = await SectionModel.objects(db)
        result = await obj.get(id=section_id)
        if result:
            return result
        else:
            raise FileNotFoundError
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail={
                "field_name": "{section_id}",
                "message": f"<{section_id}> record not found in  sections"
            })
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, "could not fetch record <{section_id}>")

get.__doc__ = f" Get a specific section by its id".expandtabs()


# query sections
@router.post('/q', tags=['sections'], status_code=HTTP_200_OK, summary="Query sections: Projection, Limit/skips, Sorting, Filters, Joins, Aggregates, Count, Group")
async def query(q: QuerySchema, db: Session = Depends(get_sync_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-sections-list', 'zekoder-zestudio-sections-get'])
    
    try:
        size = q.limit if q.limit else 20
        page = int(q.skip)/size if q.skip else 1
        jq = JSONQ(db, SectionModel)
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



# create section
@router.post('/', tags=['sections'], status_code=HTTP_201_CREATED, summary="Create new section", response_model=ReadSection)
async def create(request: Request, section: CreateSection, db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-sections-create']) 
    
    try:
        await SectionModel.validate_unique_type_app(db, section.type, section.app)
        new_data = section.dict()
        kwargs = {
            "model_data": new_data,
            "signal_data": {
                "jwt": token.credentials,
                "new_data": new_data,
                "old_data": {},
                "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
            }
        }
        obj = await SectionModel.objects(db)
        new_section = await obj.create(**kwargs)
        return new_section
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.args[-1])
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, f"creation of new section failed")

create.__doc__ = f" Create a new section".expandtabs()


# create multiple sections
@router.post('/add-sections', tags=['sections'], status_code=HTTP_201_CREATED, summary="Create multiple sections", response_model=List[ReadSection])
async def create_multiple_sections(request: Request, sections: List[CreateSection], db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-sections-create']) 
    
    new_items, errors_info = [], []
    try:
        for section_index, section in enumerate(sections):
            try:
                await SectionModel.validate_unique_type_app(db, section.type, section.app)
                new_data = section.dict()
                kwargs = {
                    "model_data": new_data,
                    "signal_data": {
                        "jwt": token.credentials,
                        "new_data": new_data,
                        "old_data": {},
                        "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
                    }
                }
                obj = await SectionModel.objects(db)
                new_sections = await obj.create(only_add=True, **kwargs)
                new_items.append(new_sections)
            except HTTPException as e:
                errors_info.append({"index": section_index, "errors": e.detail})

        if errors_info:
            return JSONResponse(errors_info, 422)
        return new_items
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.args[-1])
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, f"creation of new sections failed")

create.__doc__ = f" Create multiple new sections".expandtabs()


# upsert multiple sections
@router.post('/upsert-multiple-sections', tags=['sections'], status_code=HTTP_201_CREATED, summary="Upsert multiple sections", response_model=List[ReadSection])
async def upsert_multiple_sections(request: Request, sections: List[UpsertSection], db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-sections-create'])
    new_items, errors_info = [], []
    try:
        for section_index, section in enumerate(sections):
            try:
                await SectionModel.validate_unique_type_app(db, section.type, section.app)
                new_data = section.dict()
                kwargs = {
                    "model_data": new_data,
                    "signal_data": {
                        "jwt": token.credentials,
                        "new_data": new_data,
                        "old_data": {},
                        "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
                    }
                }
                obj = await SectionModel.objects(db)
                old_data = await obj.get(id=new_data['id'])
                if old_data:
                    kwargs['signal_data']['old_data'] = dict(old_data.__dict__) if old_data else {}
                    obj = await SectionModel.objects(db)
                    updated_sections = await obj.update(obj_id=new_data['id'], **kwargs)
                    new_items.append(updated_sections)
                else:
                    obj = await SectionModel.objects(db)
                    new_sections = await obj.create(only_add=True, **kwargs)
                    new_items.append(new_sections)
            except HTTPException as e:
                errors_info.append({"index": section_index, "errors": e.detail})

        if errors_info:
            return JSONResponse(errors_info, 422)
        return new_items
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.args[-1])
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, f"upsert multiple sections failed")

upsert_multiple_sections.__doc__ = f" upsert multiple sections".expandtabs()


# update section
@router.put('/section_id', tags=['sections'], status_code=HTTP_201_CREATED, summary="Update section with ID")
async def update(request: Request, section_id: Union[str, int], section: UpdateSection, db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-sections-update'])
    try:
        await SectionModel.validate_unique_type_app(db, section.type, section.app, section_id)
        obj = await SectionModel.objects(db)
        old_data = await obj.get(id=section_id)
        new_data = section.dict(exclude_unset=True)
        kwargs = {
            "model_data": new_data,
            "signal_data": {
                "jwt": token.credentials,
                "new_data": new_data,
                "old_data": dict(old_data.__dict__) if old_data else {},
                "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
            }
        }
        obj = await SectionModel.objects(db)
        result = await obj.update(obj_id=section_id, **kwargs)
        return result
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.args[-1])
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, "failed updating session with id <{session_id}>")

update.__doc__ = f" Update a section by its id and payload".expandtabs()


# delete section
@router.delete('/section_id', tags=['sections'], status_code=HTTP_204_NO_CONTENT, summary="Delete section with ID", response_class=Response)
async def delete(request: Request, section_id: Union[str, int], db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-sections-delete'])
    try:
        obj = await SectionModel.objects(db)
        old_data = await obj.get(id=section_id)
        kwargs = {
            "model_data": {},
            "signal_data": {
                "jwt": token.credentials,
                "new_data": {},
                "old_data": dict(old_data.__dict__) if old_data else {},
                "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
            }
        }
        obj = await SectionModel.objects(db)
        await obj.delete(obj_id=section_id, **kwargs)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail={
                "field_name": "{section_id}",
                "message": f"<{section_id}> record not found in  sections"
            })
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, "failed updating session with id <{session_id}>")

delete.__doc__ = f" Delete a section by its id".expandtabs()


# delete multiple sections
@router.delete('/delete-sections', tags=['sections'], status_code=HTTP_204_NO_CONTENT, summary="Delete multiple sections with IDs", response_class=Response)
async def delete_multiple_sections(request: Request, sections_id: List[str] = QueryParam(), db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-sections-delete'])
    kwargs = {
        "model_data": {},
        "signal_data": {
            "jwt": token.credentials,
            "new_data": {},
            "old_data": {},
            "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
        }
    }
    obj = await SectionModel.objects(db)
    await obj.delete_multiple(obj_ids=sections_id, **kwargs)

delete.__doc__ = f" Delete multiple sections by list of ids".expandtabs()

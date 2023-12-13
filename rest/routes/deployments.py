from typing import Union, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response, Query as QueryParam
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from starlette.status import HTTP_204_NO_CONTENT, HTTP_200_OK, HTTP_201_CREATED

from business.deployments_schema import *
from business.deployments_model import DeploymentModel

from core.depends import CommonDependencies, get_async_db, get_sync_db, Protect, zeauth_url
from core.logger import log
from core.query import *
from actions import deploy_solution
from business.deployments_model import DeploymentModel


router = APIRouter()


  
# list deployments
@router.get('/', tags=['deployments'], status_code=HTTP_200_OK, summary="List deployments", response_model=ReadDeployments)
async def list(request: Request, token: str = Depends(Protect), db: AsyncSession = Depends(get_async_db), commons: CommonDependencies = Depends(CommonDependencies)):
    token.auth(['zekoder-zestudio-deployments-list', 'zekoder-zestudio-deployments-get'])
    try:
        obj = await DeploymentModel.objects(db)
        result = await obj.all(offset=commons.offset, limit=commons.size)
        return {
            'data': result,
            'page_size': commons.size,
            'next_page': int(commons.page) + 1
        }
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, "could not fetch list of deployment")

list.__doc__ = f" List deployments".expandtabs()


# get deployment
@router.get('/deployment_id', tags=['deployments'], status_code=HTTP_200_OK, summary="Get deployment with ID", response_model=ReadDeployment)
async def get(request: Request, deployment_id: str, db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-deployments-list', 'zekoder-zestudio-deployments-get'])
    try:
        obj = await DeploymentModel.objects(db)
        result = await obj.get(id=deployment_id)
        if result:
            return result
        else:
            raise FileNotFoundError
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail={
                "field_name": "{deployment_id}",
                "message": f"<{deployment_id}> record not found in  deployments"
            })
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, "could not fetch record <{deployment_id}>")

get.__doc__ = f" Get a specific deployment by its id".expandtabs()


# query deployments
@router.post('/q', tags=['deployments'], status_code=HTTP_200_OK, summary="Query deployments: Projection, Limit/skips, Sorting, Filters, Joins, Aggregates, Count, Group")
async def query(q: QuerySchema, db: Session = Depends(get_sync_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-deployments-list', 'zekoder-zestudio-deployments-get'])
    
    try:
        size = q.limit if q.limit else 20
        page = int(q.skip)/size if q.skip else 1
        jq = JSONQ(db, DeploymentModel)
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



# create deployment
@router.post('/', tags=['deployments'], status_code=HTTP_201_CREATED, summary="Create new deployment", response_model=ReadDeployment)
async def create(request: Request, deployment: CreateDeployment, db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-deployments-create']) 
    
    try:
        new_data = deployment.dict()
        kwargs = {
            "model_data": new_data,
            "signal_data": {
                "jwt": token.credentials,
                "new_data": new_data,
                "old_data": {},
                "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
            }
        }
        obj = await DeploymentModel.objects(db)
        new_deployment = await obj.create(**kwargs)
        return new_deployment
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.args[-1])
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, f"creation of new deployment failed")

create.__doc__ = f" Create a new deployment".expandtabs()


# create multiple deployments
@router.post('/add-deployments', tags=['deployments'], status_code=HTTP_201_CREATED, summary="Create multiple deployments", response_model=List[ReadDeployment])
async def create_multiple_deployments(request: Request, deployments: List[CreateDeployment], db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-deployments-create']) 
    
    new_items, errors_info = [], []
    try:
        for deployment_index, deployment in enumerate(deployments):
            try:
                new_data = deployment.dict()
                kwargs = {
                    "model_data": new_data,
                    "signal_data": {
                        "jwt": token.credentials,
                        "new_data": new_data,
                        "old_data": {},
                        "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
                    }
                }
                obj = await DeploymentModel.objects(db)
                new_deployments = await obj.create(only_add=True, **kwargs)
                new_items.append(new_deployments)
            except HTTPException as e:
                errors_info.append({"index": deployment_index, "errors": e.detail})

        return new_items
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.args[-1])
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, f"creation of new deployments failed")

create.__doc__ = f" Create multiple new deployments".expandtabs()


# upsert multiple deployments
@router.post('/upsert-multiple-deployments', tags=['deployments'], status_code=HTTP_201_CREATED, summary="Upsert multiple deployments", response_model=List[ReadDeployment])
async def upsert_multiple_deployments(request: Request, deployments: List[UpsertDeployment], db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-deployments-create'])
    new_items, errors_info = [], []
    try:
        for deployment_index, deployment in enumerate(deployments):
            try:
                new_data = deployment.dict()
                kwargs = {
                    "model_data": new_data,
                    "signal_data": {
                        "jwt": token.credentials,
                        "new_data": new_data,
                        "old_data": {},
                        "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
                    }
                }
                obj = await DeploymentModel.objects(db)
                old_data = await obj.get(id=new_data['id'])
                if old_data:
                    kwargs['signal_data']['old_data'] = dict(old_data.__dict__) if old_data else {}
                    obj = await DeploymentModel.objects(db)
                    updated_deployments = await obj.update(obj_id=new_data['id'], **kwargs)
                    new_items.append(updated_deployments)
                else:
                    obj = await DeploymentModel.objects(db)
                    new_deployments = await obj.create(only_add=True, **kwargs)
                    new_items.append(new_deployments)
            except HTTPException as e:
                errors_info.append({"index": deployment_index, "errors": e.detail})

        return new_items
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.args[-1])
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, f"upsert multiple deployments failed")

upsert_multiple_deployments.__doc__ = f" upsert multiple deployments".expandtabs()


# update deployment
@router.put('/deployment_id', tags=['deployments'], status_code=HTTP_201_CREATED, summary="Update deployment with ID")
async def update(request: Request, deployment_id: Union[str, int], deployment: UpdateDeployment, db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-deployments-update'])
    try:
        obj = await DeploymentModel.objects(db)
        old_data = await obj.get(id=deployment_id)
        new_data = deployment.dict(exclude_unset=True)
        kwargs = {
            "model_data": new_data,
            "signal_data": {
                "jwt": token.credentials,
                "new_data": new_data,
                "old_data": dict(old_data.__dict__) if old_data else {},
                "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
            }
        }
        obj = await DeploymentModel.objects(db)
        result = await obj.update(obj_id=deployment_id, **kwargs)
        return result
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(422, e.orig.args[-1])
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, "failed updating session with id <{session_id}>")

update.__doc__ = f" Update a deployment by its id and payload".expandtabs()


# delete deployment
@router.delete('/deployment_id', tags=['deployments'], status_code=HTTP_204_NO_CONTENT, summary="Delete deployment with ID", response_class=Response)
async def delete(request: Request, deployment_id: Union[str, int], db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-deployments-delete'])
    try:
        obj = await DeploymentModel.objects(db)
        old_data = await obj.get(id=deployment_id)
        kwargs = {
            "model_data": {},
            "signal_data": {
                "jwt": token.credentials,
                "new_data": {},
                "old_data": dict(old_data.__dict__) if old_data else {},
                "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
            }
        }
        obj = await DeploymentModel.objects(db)
        await obj.delete(obj_id=deployment_id, **kwargs)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail={
                "field_name": "{deployment_id}",
                "message": f"<{deployment_id}> record not found in  deployments"
            })
    except Exception as e:
        log.debug(e)
        raise HTTPException(500, "failed updating session with id <{session_id}>")

delete.__doc__ = f" Delete a deployment by its id".expandtabs()


# delete multiple deployments
@router.delete('/delete-deployments', tags=['deployments'], status_code=HTTP_204_NO_CONTENT, summary="Delete multiple deployments with IDs", response_class=Response)
async def delete_multiple_deployments(request: Request, deployments_id: List[str] = QueryParam(), db: AsyncSession = Depends(get_async_db), token: str = Depends(Protect)):
    token.auth(['zekoder-zestudio-deployments-delete'])
    kwargs = {
        "model_data": {},
        "signal_data": {
            "jwt": token.credentials,
            "new_data": {},
            "old_data": {},
            "well_known_urls": {"zeauth": zeauth_url, "self": str(request.base_url)}
        }
    }
    obj = await DeploymentModel.objects(db)
    await obj.delete_multiple(obj_ids=deployments_id, **kwargs)

delete.__doc__ = f" Delete multiple deployments by list of ids".expandtabs()

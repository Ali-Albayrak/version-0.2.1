import os
import uuid
from contextvars import ContextVar
from typing import Optional

import requests as prequest
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from business import db_async_session, db_sync_session
from core.logger import log

auth_schema = HTTPBearer()
zeauth_url = os.environ.get('ZEAUTH_URI', 'https://zekoder-zeauth-dev-25ahf2meja-uc.a.run.app')
user_session: ContextVar[str] = ContextVar('user_session', default=None)
user_roles: ContextVar[list] = ContextVar('user_roles', default=[])

async def get_async_db():
    async with db_async_session() as db:
        try:
            # set session variables
            await db.execute(f"SET zekoder.id = '{current_user_uuid()}'")
            await db.execute(f"SET zekoder.roles = '{','.join(current_user_roles())}'")

            yield db
        # except ConnectionRefusedError as e:
        #     log.debug(f"error: {e.args[-1]}")
        #     raise HTTPException(503, e.args)
        finally:
            await db.close()

def get_sync_db():
    db = db_sync_session()
    try:
        # set session variables
        db.execute(f"SET zekoder.id = '{current_user_uuid()}'")
        db.execute(f"SET zekoder.roles = '{','.join(current_user_roles())}'")
        yield db
    finally:
        db.close()


class CommonDependencies:
    def __init__(self, page: Optional[str] = 1, size: Optional[int] = 20):
        self.page = page
        self.size = size
        self.offset = (int(page)-1) * int(size)


class Protect:
    def __init__(self, token: str = Depends(auth_schema), db: Session = Depends(get_async_db)) -> None:
        self.credentials = token.credentials
        self.db = db

    def auth(self, method_required_permissions):
        response = prequest.request("POST", f"{zeauth_url}/verify?token={self.credentials}", data={})
        if response.status_code != 200:
            raise HTTPException(403, "invalid token")
        has_permission = False
        for permission in method_required_permissions:
            if permission in response.json()['permissions']:
                has_permission = True
                break
        if not has_permission:
            raise HTTPException(403, "user not authorized to do this action")
        self.set_current_user_uuid_in_contextvar(response=response)
        return response

    def set_current_user_uuid_in_contextvar(self, response):
        try:
            current_user = response.json()
            log.debug(f"current user: {current_user}")
            current_user_id = current_user.get("id")
            current_user_roles_ = current_user.get("roles", [])
            if not current_user_id:
                raise
            user_session.set(current_user_id)
            user_roles.set(current_user_roles_)
        except Exception as e:
            log.debug(e)
            raise HTTPException(403, "user not authorized to do this action")


def current_user_uuid():
    """
    get current user uuid from contextvar
    """
    log.debug(f"user_session: {user_session}")
    return user_session.get()


def current_user_roles() -> list:
    """
    get current user roles from contextvar
    """
    return user_roles.get()

import json
from core.logger import log
from sqlalchemy.ext.asyncio import AsyncSession 
from sqlalchemy import select, delete, update, insert

from core.depends import current_user_roles, current_user_uuid, get_async_db

class Manager:

    def __init__(self, model, database: AsyncSession):
        if not database:
            database = next(get_async_db())
        self.db = database
        self.Model = model
        self._query = {}  # Instantiate a query, update it on get/filter call
    
    async def set_session_vars(self):
        await self.db.execute(f"SET zekoder.id = '{current_user_uuid()}'")
        await self.db.execute(f"SET zekoder.roles = '{','.join(current_user_roles())}'")

    @classmethod
    async def async_init(cls, model, database: AsyncSession):
        obj = cls(model,database)
        await obj.set_session_vars()
        return obj

    def __str__(self):
        return "%s_%s" % (self.__class__.__name__, self.Model.__name__)

    async def __len__(self):
        data = await self.__fetch()
        return len(data.scalars().all())

    async def __iter__(self):
        data = await self.__fetch()
        for obj in data.scalars().all():
            yield obj

    def __getitem__(self, item):
        return list(self)[item]

    def update_query(self, query):
        self._query.update(query)

    async def __fetch(self):
        return await self.db.execute(select(self.Model).filter_by(**self._query))

    async def get(self, **query):
        self.update_query(query)
        data = await self.__fetch()
        return data.scalars().first()

    def filter(self, **query):
        self.update_query(query)
        return self

    async def create(self, only_add: bool = False, **kwargs):
        model_data = kwargs.get("model_data", {})
        if kwargs.get("signal_data"):
            model_data.update(await self.pre_save(**kwargs["signal_data"]))
        obj = self.Model(**model_data)
        # if only_add:  # to handle multi-create in on commit
        #     self.db.add(obj)
        #     return obj
        await self.save(obj)
        if kwargs.get("signal_data"):
            try:
                kwargs.get("signal_data")["new_data"] = obj.__dict__
                await self.post_save(**kwargs["signal_data"])
            except Exception as e:
                log.debug(e)

        return obj

    async def save(self, obj):
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)

    async def update(self, obj_id, **kwargs):
        model_data = kwargs.get("model_data", {})
        if kwargs.get("signal_data"):
            model_data.update(await self.pre_update(**kwargs["signal_data"]))
        statement = update(self.Model)\
                    .filter(self.Model.id == obj_id)\
                    .values(model_data)\
                    .returning(self.Model.__table__)
        updated_row = await self.db.execute(statement)
        await self.db.commit()
        try:
            if kwargs.get("signal_data"):
                kwargs.get("signal_data")["new_data"] = model_data
                await self.post_update(**kwargs["signal_data"])
        except Exception as e:
            log.debug(e)
        return updated_row

    async def delete(self, obj_id, **kwargs):
        is_delete = True
        if kwargs.get("signal_data"):
            is_delete = await self.pre_delete(**kwargs["signal_data"])
        if not is_delete:
            return
        await self.db.execute(delete(self.Model).filter(self.Model.id == obj_id))
        await self.db.commit()
        try:
            if kwargs.get("signal_data"):
                kwargs.get("signal_data")["new_data"] = is_delete
                await self.post_delete(**kwargs["signal_data"])
        except Exception as e:
            log.debug(e)

    async def delete_multiple(self, obj_ids: list, **kwargs):
        is_delete = True
        if kwargs.get("signal_data"):
            is_delete = self.pre_delete(**kwargs["signal_data"])
        if not is_delete:
            return
        await self.db.execute(delete(self.Model).filter(self.Model.id.in_(obj_ids)))
        await self.db.commit()

    async def pre_save(self, **kwargs):
        return kwargs.get("new_data")

    async def post_save(self, **kwargs):
        pass

    async def pre_update(self, **kwargs):
        return kwargs.get("new_data")

    async def post_update(self, **kwargs):
        pass

    async def pre_delete(self, **kwargs):
        return True

    async def post_delete(self, **kwargs):
        pass

    async def all(self, offset: int = 0, limit: int = 10, **query):
        self.update_query(query)
        data = await self.__fetch()
        data = data.scalars().all()
        return data[offset*limit:(offset+1)*limit]
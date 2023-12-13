import json
from core.logger import log
from sqlalchemy.ext.asyncio import AsyncSession 
from sqlalchemy import select, delete, update, insert
from core.depends import current_user_roles, current_user_uuid, get_async_db

class Manager:
    """
    A generic database interaction class for handling CRUD operations on a specified model.
    """

    def __init__(self, model, database: AsyncSession):
        if not database:
            database = next(get_async_db())
        self.db = database
        self.Model = model
        self._query = {}  # Instantiate a query, update it on get/filter call

    @classmethod
    async def async_init(cls, model, database: AsyncSession):
        """
        Asynchronously initialize an instance of the class
        """
        obj = cls(model, database)
        await obj.set_session_vars()
        return obj
    
    async def set_session_vars(self):
        """
        Set session variables for the instance
        """
        await self.db.execute(f"SET zekoder.id = '{current_user_uuid()}'")
        await self.db.execute(f"SET zekoder.roles = '{','.join(current_user_roles())}'")

    def __str__(self):
        """
        Return a string representation of the instance
        """
        return "%s_%s" % (self.__class__.__name__, self.Model.__name__)

    async def __len__(self):
        """
        Return the number of records in the database based on the current query.
        """
        data = await self.__fetch()
        return len(data.scalars().all())
    
    async def __iter__(self):
        """
        Iterate over the records fetched from the database based on the current query.
        """
        data = await self.__fetch()
        for obj in data.scalars().all():
            yield obj

    def __getitem__(self, item):
        """
        Get an item from the records fetched from the database.
        """
        return list(self)[item]

    def update_query(self, query):
        """
        Update the query for the instance.
        """
        self._query.update(query)

    async def __fetch(self):
        """
        Asynchronously fetch records from the database based on the current query.
        """
        return await self.db.execute(select(self.Model).filter_by(**self._query))
    
    async def get(self, **query):
        """
        Get a single record from the database based on the provided query.
        """
        self.update_query(query)
        data = await self.__fetch()
        return data.scalars().first()
    
    def filter(self, **query):
        """
        Update the query for filtering records.
        """
        self.update_query(query)
        return self

    async def create(self, only_add: bool = False, **kwargs):
        """
        Create a new record in the database.
        """
        model_data = kwargs.get("model_data", {})
        if kwargs.get("signal_data"):
            model_data.update(await self.pre_save(**kwargs["signal_data"]))
        obj = self.Model(**model_data)
        await self.save(obj)
        if kwargs.get("signal_data"):
            try:
                kwargs.get("signal_data")["new_data"] = obj.__dict__
                await self.post_save(**kwargs["signal_data"])
            except Exception as e:
                log.debug(e)

        return obj

    async def save(self, obj):
        """
        Save changes to the database after adding a new record.
        """
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)

    async def update(self, obj_id, **kwargs):
        """
        Update an existing record in the database.
        """
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
        """
        Delete a record from the database.
        """
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
        """
        Delete multiple records from the database.
        """
        is_delete = True
        if kwargs.get("signal_data"):
            is_delete = self.pre_delete(**kwargs["signal_data"])
        if not is_delete:
            return
        await self.db.execute(delete(self.Model).filter(self.Model.id.in_(obj_ids)))
        await self.db.commit()

    async def pre_save(self, **kwargs):
        """
        Perform pre-save operations and return additional model data.
        """
        return kwargs.get("new_data")

    async def post_save(self, **kwargs):
        """
        Perform post-save operations.
        """
        pass

    async def pre_update(self, **kwargs):
        """
        Perform pre-update operations and return additional model data.
        """
        return kwargs.get("new_data")

    async def post_update(self, **kwargs):
        """
        Perform post-update operations.
        """
        pass

    async def pre_delete(self, **kwargs):
        """
        Perform pre-delete operations and return a boolean indicating whether to proceed with the delete.
        """
        return True

    async def post_delete(self, **kwargs):
        """
        Perform post-delete operations.
        """
        pass

    async def all(self, offset: int = 0, limit: int = 10, **query):
        """
        Retrieve all records from the database based on the current query, with optional offset and limit.
        """
        self.update_query(query)
        data = await self.__fetch()
        data = data.scalars().all()
        return data[offset*limit:(offset+1)*limit]

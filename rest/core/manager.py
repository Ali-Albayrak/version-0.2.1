import json
from core.logger import log
from sqlalchemy.orm import Session

from core.depends import get_db, current_user_uuid, current_user_roles


class Manager:

    def __init__(self, model, database: Session):
        if not database:
            database = next(get_db())
        self.db = database
        self.Model = model
        self._query = {}  # Instantiate a query, update it on get/filter call
        # set session variables
        self.db.execute(f"SET zekoder.id = '{current_user_uuid()}'")
        self.db.execute(f"SET zekoder.roles = '{','.join(current_user_roles())}'")

    def __str__(self):
        return "%s_%s" % (self.__class__.__name__, self.Model.__name__)

    def __len__(self):
        return self.__fetch().count()

    def __iter__(self):
        for obj in self.__fetch():
            yield obj

    def __getitem__(self, item):
        return list(self)[item]

    def update_query(self, query):
        self._query.update(query)

    def __fetch(self):
        return self.db.query(self.Model).filter_by(**self._query)

    def get(self, **query):
        self.update_query(query)
        return self.__fetch().first()

    def filter(self, **query):
        self.update_query(query)
        return self

    def create(self, only_add: bool = False, **kwargs):
        model_data = kwargs.get("model_data", {})
        if kwargs.get("signal_data"):
            model_data.update(self.pre_save(**kwargs["signal_data"]))
        obj = self.Model(**model_data)
        if only_add:  # to handle multi-create in on commit
            self.db.add(obj)
            return obj
        self.save(obj)
        if kwargs.get("signal_data"):
            try:
                kwargs.get("signal_data")["new_data"] = obj.__dict__
                self.post_save(**kwargs["signal_data"])
            except Exception as e:
                log.debug(e)

        return obj

    def save(self, obj):
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)

    def update(self, obj_id, **kwargs):
        model_data = kwargs.get("model_data", {})
        if kwargs.get("signal_data"):
            model_data.update(self.pre_update(**kwargs["signal_data"]))
        self.db.query(self.Model).filter(self.Model.id == obj_id).update(model_data)
        self.db.commit()
        try:
            if kwargs.get("signal_data"):
                kwargs.get("signal_data")["new_data"] = model_data
                self.post_update(**kwargs["signal_data"])
        except Exception as e:
            log.debug(e)

    def delete(self, obj_id, **kwargs):
        delete = True
        if kwargs.get("signal_data"):
            delete = self.pre_delete(**kwargs["signal_data"])
        if not delete:
            return
        self.db.query(self.Model).filter(self.Model.id == obj_id).delete()
        self.db.commit()
        try:
            if kwargs.get("signal_data"):
                kwargs.get("signal_data")["new_data"] = delete
                self.post_delete(**kwargs["signal_data"])
        except Exception as e:
            log.debug(e)

    def delete_multiple(self, obj_ids: list, **kwargs):
        delete = True
        if kwargs.get("signal_data"):
            delete = self.pre_delete(**kwargs["signal_data"])
        if not delete:
            return
        self.db.query(self.Model).filter(self.Model.id.in_(obj_ids)).delete(synchronize_session=False)
        self.db.commit()

    def pre_save(self, **kwargs):
        return kwargs.get("new_data")

    def post_save(self, **kwargs):
        pass

    def pre_update(self, **kwargs):
        return kwargs.get("new_data")

    def post_update(self, **kwargs):
        pass

    def pre_delete(self, **kwargs):
        return True

    def post_delete(self, **kwargs):
        pass

    def all(self, offset: int = 0, limit: int = 10, **query):
        self.update_query(query)
        return self.__fetch().offset(offset).limit(limit).all()

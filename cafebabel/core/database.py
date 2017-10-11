'''
Override peewee Database to use playhouse signals by default with
a configurable database setting.
'''

from flask_peewee.db import Database as _Database
from playhouse.signals import Model


class Database(_Database):
    def get_model_class(self):
        class BaseModel(Model):
            class Meta:
                database = self.database

        return BaseModel

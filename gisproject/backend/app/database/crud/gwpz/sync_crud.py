
from app.database.crud.base.sync_base import CrudBase
from sqlalchemy.orm import Session
from app.database.models import GWQI_Threshold

class WQI_threshold(CrudBase):
    def __init__(self,db: Session,Model=GWQI_Threshold):
        super().__init__(db,Model)
        self.obj = None

    def get_threshold(self):
        query= self.db.query(self.Model)
        return self._pagination(query, True)
    

from app.database.models import RasterMetadata,UserStorage,VectorMetadata
from app.database.crud.base.sync_base import CrudBase
from sqlalchemy.orm import Session
from app.api.schema.raster_operation import useroperSchema,rasterMetaSchame,vectorMetaSchema


class userstorecrud(CrudBase):
    def __init__(self,db:Session,Model=UserStorage):
        super().__init__(db,Model)
        self.obj=None

    def get_details(self,file_id:str):
        return self.db.query(self.Model).filter(self.Model.file_id==file_id).first()

    def create_details(self,payload:useroperSchema):
        return self.create(payload.model_dump())

class rasterMetacrud(CrudBase):
    def __init__(self,db:Session,Model=RasterMetadata):
        super().__init__(db,Model)
        self.obj=None

    def get_details(self,file_id:str):
        return self.db.query(self.Model).filter(self.Model.file_id==file_id).first()
    
    def create_details(self,payload:rasterMetaSchame):
        return self.create(payload.model_dump())
    

class vectorMetacrud(CrudBase):
    def __init__(self,db:Session,Model=VectorMetadata):
        super().__init__(db,Model)
        self.obj=None

    def get_details(self,file_id:str):
        return self.db.query(self.Model).filter(self.Model.file_id==file_id).first()
    
    def create_details(self,payload:vectorMetaSchema):
        return self.create(payload.model_dump())
    

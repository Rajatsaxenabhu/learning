from sqlalchemy.orm import Session, joinedload, contains_eager
from app.database.crud.base.sync_base import CrudBase
from app.database.models.workspace import (ModuleLayerDefinition, UserDataStorage, Workspace,
                                            Module,
                                            GlobalRaster,WorkspaceAdminLocation,
                                            WorkspaceDrainLocation, WorkspaceLayers, WorkspaceModule)
class WorkspaceCrud(CrudBase):
    def __init__(self,db:Session,Model=Workspace):
        self.db=db
        self.Model=Model
        self.obj=None

    def get_all(self,all_data:bool=True):
        query=self.db.query(self.Model).filter()
        return self._pagination(query,all_data)
    
    def get_workspace(self,user_id:int,all_data:bool=True):
        query=self.db.query(self.Model).filter(
            self.Model.user_id==user_id
        )
        return self._pagination(query,all_data)
    
    def new_workspace(self,payload:dict):
        return self.create(payload)
    
    def delete_workspace(self,id:int):
        return self.delete(id)

    def getworspaceById(self,work_id:int,all_data:bool=True):
        query = self.db.query(self.Model).filter(self.Model.id == work_id)
        return self._pagination(query,all_data)

class WorkspaceModuleCrud(CrudBase):
    def __init__(self,db:Session,Model=WorkspaceModule):
        self.db=db
        self.Model=Model
        self.obj=None
    
    def make_workspace_module(self,payload:dict):
        return self.create(payload)




class ModuleCrud(CrudBase):
    def __init__(self,db:Session,Model=Module):
        self.db=db
        self.Model=Model
        self.obj=None

    def get_all(self,all_data:bool=True):
        query=self.db.query(self.Model)
        return self._pagination(query,all_data)
    
    def get_names(self,all_data:bool=True):
        query=self.db.query(self.Model.name).distinct()
        results= self._pagination(query,all_data)
        return [row[0] for row in results]
    
    def get_module_byid(self,model_id:int):
        query=self.db.query(self.Model).filter(
            self.Model.id==model_id
        )
        return query.first()

    def get_by_name(self, name: str):
        query = self.db.query(self.Model).filter(self.Model.name == name)
        return query.first()

class LayerCrud(CrudBase):
    def __init__(self,db:Session,Model=GlobalRaster):
        self.db=db
        self.Model=Model
        self.obj=None

    def get_all(self,all_data:bool=True):
        query=self.db.query(self.Model)
        return self._pagination(query,all_data)
    
class Adminlocationcrud(CrudBase):
    def __init__(self,db:Session,Model=WorkspaceAdminLocation):
        self.db=db
        self.Model=Model
        self.obj=None

    def get_location(self,workspace_id:int,all_data:bool=True):
        query=self.db.query(self.Model).filter(
            self.Model.workspace_id==workspace_id
        )
        return self._pagination(query,all_data)

    def set_location(self,payload:dict):
        return self.create(payload)
    
    
class Drainlocationcrud(CrudBase):
    def __init__(self,db:Session,Model=WorkspaceDrainLocation):
        self.db=db
        self.Model=Model
        self.obj=None

    def get_location(self,workspace_id:int,all_data:bool=True):
        query=self.db.query(self.Model).filter(
            self.Model.workspace_id==workspace_id
        )
        return self._pagination(query,all_data)

    def set_location(self,payload:dict):
        return self.create(payload)
    



class GlobalLayerCrud(CrudBase):
    def __init__(self,db:Session,Model=GlobalRaster):
        self.db=db
        self.Model=Model
        self.obj=None

    def get_module_layer(self, module_id: int):
        query = (self.db.query(ModuleLayerDefinition)
            .options(joinedload(ModuleLayerDefinition.global_raster))
            .filter(ModuleLayerDefinition.module_id == module_id))
        return self._pagination(query)
       
class WorkspaceLayersCrud(CrudBase):
    def __init__(self, db: Session, Model=WorkspaceLayers):
        self.db = db
        self.Model = Model
        self.obj = None

    def get_layer(self, workspace_id: int):
        query=self.db.query(self.Model).filter(
            self.Model.workspace_id==workspace_id
        )
        return self._pagination(query,True)
    
    def get_layer_by_id(self,layer_id:list):
        query=self.db.query(self.Model).options(joinedload(self.Model.module_layer_def)).filter(self.Model.id.in_(layer_id))
        return self._pagination(query,True)
    
    def push_layer(self, data: list):
        self.create_many(data)

    def get_workspace_layers(self, workspace_id: int,is_internal:bool=False):
        query = (self.db.query(self.Model)
                .join(self.Model.module_layer_def)
                .options(contains_eager(self.Model.module_layer_def))
                .filter(self.Model.workspace_id == workspace_id,ModuleLayerDefinition.is_internal==is_internal)
        )
        return self._pagination(query)
    
    def update_layer(self, payload: dict):
        return self.update(payload)
    
class UserStorageCrud(CrudBase):
    def __init__(self,db:Session,Model=UserDataStorage):
        self.db=db
        self.Model=Model
        self.obj = None

    def push_data(self,payload:dict):
        return self.create(payload)
    
    def get_media_path(self,unq_name:str):
        query = self.db.query(self.Model).filter(self.Model.unq_name == unq_name)
        return self._pagination(query,True)

class ModuleLayerDefinitionCrud(CrudBase):
    def __init__(self, db: Session, Model=ModuleLayerDefinition):
        self.db = db
        self.Model = Model
        self.obj = None

    def get_module_layer(self, module_id: int):
        query = self.db.query(self.Model).filter(self.Model.module_id == module_id)
        return self._pagination(query,True)
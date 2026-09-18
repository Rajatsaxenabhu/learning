from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.database.crud.base.async_base import CrudBase
from app.database.models.workspace import (ModuleLayerDefinition, Project, ProjectData, UserDataStorage, Workspace,
                                            Module,
                                            GlobalRaster, WorkspaceAdminLocation,
                                            WorkspaceDrainLocation, WorkspaceLayers, WorkspaceModule)
from sqlalchemy.orm import joinedload, selectinload, contains_eager


class WorkspaceCrud(CrudBase):
    def __init__(self, db: AsyncSession, Model=Workspace):
        self.db = db
        self.Model = Model
        self.obj = None

    async def get_all(self, all_data: bool = True):
        query = select(self.Model)
        return await self._pagination(self.db, query, all_data)

    async def get_workspace(self, user_id: int, all_data: bool = True):
        query = select(self.Model).filter(self.Model.user_id == user_id)
        return await self._pagination(self.db, query, all_data)
    
    async def get_module_workspace(self, user_id: int,module_id:int, all_data: bool = True):
        query = select(self.Model).join(WorkspaceModule,WorkspaceModule.workspace_id==self.Model.id).filter(self.Model.user_id == user_id,WorkspaceModule.module_id==module_id)
        return await self._pagination(self.db, query, all_data)
    

    async def getworspaceById(self,work_id:int,all_data:bool=True):
        query = select(self.Model).filter(self.Model.id == work_id)
        return await self._pagination(self.db, query, all_data)

    async def new_workspace(self, payload: dict):
        return await self.create(payload)

    async def delete_workspace(self, id: int):
        return await self.delete(id)

class ProjectCrud(CrudBase):
    def __init__(self, db: AsyncSession, Model=Project):
        self.db = db
        self.Model = Model
        self.obj = None

    async def create_new(self,payload:dict):
        return await self.create(payload)
    
    async def load_project(self,workspace_id:int,module_id:int):
        query=(
            select(self.Model)
            .options(selectinload(self.Model.data))
            .filter(self.Model.workspace_id==workspace_id)
            .filter(self.Model.module_id==module_id)
        )
        return await self._pagination(self.db, query)


    
class WorkspaceModuleCrud(CrudBase):
    def __init__(self, db: AsyncSession, Model=WorkspaceModule):
        self.db = db
        self.Model = Model
        self.obj = None

    async def make_workspace_module(self, payload: dict):
        return await self.create(payload)
    async def get_workspace_module(self, workspace_id: int, all_data: bool = True):
        query = select(self.Model).filter(self.Model.workspace_id == workspace_id).order_by(self.Model.module_id)
        return await self._pagination(self.db, query, all_data)


class ModuleCrud(CrudBase):
    def __init__(self, db: AsyncSession, Model=Module):
        self.db = db
        self.Model = Model
        self.obj = None

    async def get_all(self, all_data: bool = True):
        query = select(self.Model)
        return await self._pagination(self.db, query, all_data)

    async def get_names(self, all_data: bool = True):
        query = select(self.Model.name,self.Model.id).distinct()
        result = await self.db.execute(query)
        rows = result.all()
        return [dict(row._mapping) for row in rows]

    async def get_module_byid(self, model_id: int):
        query = select(self.Model).filter(self.Model.id == model_id)
        result = await self.db.execute(query)
        return result.scalars().first()
    
    async def get_by_name(self, name: str):
        query = select(self.Model).filter(self.Model.name == name)
        result = await self.db.execute(query)
        return result.scalars().first()


class LayerCrud(CrudBase):
    def __init__(self, db: AsyncSession, Model=GlobalRaster):
        self.db = db
        self.Model = Model
        self.obj = None

    async def get_all(self, all_data: bool = True):
        query = select(self.Model.name)
        return await self._pagination(self.db, query, all_data)

    async def get_unq(self,all_data:bool=True):
        query = select(self.Model).distinct(self.Model.name)
        return await self._pagination(self.db, query, all_data)


class Adminlocationcrud(CrudBase):
    def __init__(self, db: AsyncSession, Model=WorkspaceAdminLocation):
        self.db = db
        self.Model = Model
        self.obj = None

    async def get_location(self, workspace_id: int, all_data: bool = True):
        query = select(self.Model).filter(self.Model.workspace_id == workspace_id)
        return await self._pagination(self.db, query, all_data)

    async def set_location(self, payload: dict):
        return await self.create(payload)
    



class Drainlocationcrud(CrudBase):
    def __init__(self, db: AsyncSession, Model=WorkspaceDrainLocation):
        self.db = db
        self.Model = Model
        self.obj = None

    async def get_location(self, worskpace_id: int, all_data: bool = True):
        query = select(self.Model).filter(self.Model.workspace_id == worskpace_id)
        return await self._pagination(self.db, query, all_data)

    async def set_location(self, payload: dict):
        return await self.create(payload)


class GlobalLayerCrud(CrudBase):
    def __init__(self, db: AsyncSession, Model=GlobalRaster):
        self.db = db
        self.Model = Model
        self.obj = None

    async def get_module_layer(self, module_id: int):
        query = (
            select(self.Model)
            .join(ModuleLayerDefinition, ModuleLayerDefinition.global_raster_id == self.Model.id)
            .filter(ModuleLayerDefinition.module_id == module_id)
        )
        return await self._pagination(self.db, query)
    
    async def get_all_module_layer(self):
        query = (
            select(
                self.Model.id,
                self.Model.name,
                self.Model.layer_name,
                Module.name.label("module_name"),
                Module.id.label("module_id"),
                ModuleLayerDefinition.category.label("category")
            )
            .join(ModuleLayerDefinition, ModuleLayerDefinition.global_raster_id == self.Model.id)
            .join(Module, Module.id == ModuleLayerDefinition.module_id)
            .filter(
                or_(
                    ModuleLayerDefinition.category.ilike("%condition%"),
                    ModuleLayerDefinition.category.ilike("%constraint%"),
                )
            )
        )
        result = await self.db.execute(query)
        return result.mappings().all()

    
class ModuleLayerDefinitionCrud(CrudBase):
    def __init__(self, db: AsyncSession, Model=ModuleLayerDefinition):
        self.db = db
        self.Model = Model
        self.obj = None

    async def get_module_layer(self, module_id: int):
        query = select(self.Model).filter(self.Model.module_id == module_id)
        return await self._pagination(self.db, query)

class WorkspaceLayersCrud(CrudBase):
    def __init__(self, db: AsyncSession, Model=WorkspaceLayers):
        self.db = db
        self.Model = Model
        self.obj = None

    async def get_layer(self,workspace_id:int):
        query = select(self.Model).filter(self.Model.workspace_id == workspace_id)
        return await self._pagination(self.db, query)
    

    async def get_layer_by_id(self,layer_id:list):
        query = select(self.Model).options(joinedload(self.Model.module_layer_def)).filter(self.Model.id.in_(layer_id))
        return await self._pagination(self.db, query)

    async def push_layer(self, data: list):
        await self.create_many(data)

    async def get_workspace_layers(self, workspace_id: int, is_internal: bool = False):
        query = (
            select(self.Model)
            .join(self.Model.module_layer_def)
            .options(contains_eager(self.Model.module_layer_def))
            .filter(self.Model.workspace_id == workspace_id, ModuleLayerDefinition.is_internal == is_internal)
        )
        return await self._pagination(self.db, query)
    

class UserStorageCrud(CrudBase):
    def __init__(self,db:AsyncSession,Model=UserDataStorage):
        self.db=db
        self.Model=Model
        self.obj = None

    async def push_data(self,payload:dict):
        return await self.create(payload)
    
    async def get_report_path(self,report_id:str):
        query = select(self.Model).filter(self.Model.unq_name == report_id)
        result = await self.db.execute(query)
        return result.scalars().first()
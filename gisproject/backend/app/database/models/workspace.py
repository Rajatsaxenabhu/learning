from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import UUID, String, Integer, ForeignKey, Text, Float, JSON, UniqueConstraint, Boolean
from app.database.models.base import Base
from typing import List, Optional
from sqlalchemy.dialects.postgresql import ARRAY, JSON,JSONB
import uuid

class Signup_temp(Base):
    __tablename__ = "signup_temp"
    fullname: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(50),nullable=False)
    password: Mapped[str] = mapped_column(String(200), nullable=False)
    contact_no: Mapped[str] = mapped_column(String(15), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    designation: Mapped[str] = mapped_column(String(100), nullable=False)
    organisation: Mapped[str] = mapped_column(String(50), nullable=False)
    temp_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4,unique=True,nullable=False)


class User(Base):
    __tablename__ = "users"
    fullname: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(50), unique=True,nullable=False)
    password: Mapped[str] = mapped_column(String(200), nullable=False)
    admin_level: Mapped[int] = mapped_column(Integer, nullable=False ,default=2) # 1 for admin 2 for user
    is_verified: Mapped[bool] = mapped_column(default=False, nullable=False)
    details: Mapped[Optional["UserDetails"]] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan")
    workspaces: Mapped[List["Workspace"]] = relationship(              
        back_populates="user", cascade="all, delete-orphan"
    )


class UserDetails(Base):
    __tablename__ = "user_details"
    contact_no: Mapped[str] = mapped_column(String(15), nullable=False)
    designation: Mapped[str] = mapped_column(String(100), nullable=False)
    organisation: Mapped[str] = mapped_column(String(50), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    user: Mapped["User"] = relationship(back_populates="details")



class UserDataStorage(Base):
    __tablename__ = "user_data_storage"
    data_type: Mapped[str] = mapped_column(String(50), nullable=False)
    unq_name: Mapped[str] = mapped_column(String(50), nullable=False,unique=True)
    data_path: Mapped[str] = mapped_column(String, nullable=False)
    admin_shp: Mapped[Optional["WorkspaceAdminLocation"]] = relationship(
    back_populates="admin_storage",
    uselist=False
    )
    drain_shp: Mapped[Optional["WorkspaceDrainLocation"]] = relationship(
        back_populates="drain_storage",
        uselist=False
    )


class GlobalRaster(Base):
    __tablename__ = 'global_raster'
    layer_id: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=False)
    layer_name: Mapped[str] = mapped_column(String(255), nullable=False,unique=True)
    layer_path: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sld_path:Mapped[str]=mapped_column(String,nullable=True)
    type: Mapped[str] = mapped_column(String(50), nullable=False)



class Module(Base):
    __tablename__ = 'modules'
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    admin_level: Mapped[str] = mapped_column(String(50), nullable=True) 
    drain_level: Mapped[str] = mapped_column(String(50), nullable=True)   
    config: Mapped[dict] = mapped_column(JSON, nullable=True)         
    layer_definitions: Mapped[List["ModuleLayerDefinition"]] = relationship(
        back_populates="module"
    )
    workspace_modules: Mapped[list["WorkspaceModule"]] = relationship(
    back_populates="module",
    cascade="all, delete-orphan"
    )   


    
class ModuleLayerDefinition(Base):
    __tablename__ = 'module_layer_definitions'
    module_id: Mapped[int] = mapped_column(ForeignKey('modules.id'), nullable=False)
    global_raster_id: Mapped[int]= mapped_column(
        ForeignKey("global_raster.layer_id"), nullable=False 
    )
    default_weight: Mapped[float] = mapped_column(Float, nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    is_internal: Mapped[bool] = mapped_column(default=False, nullable=False)
    module: Mapped["Module"] = relationship(back_populates="layer_definitions")
    global_raster: Mapped[Optional["GlobalRaster"]] = relationship()
    norm: Mapped[str] = mapped_column(String(50), nullable=True)


class WorkspaceAdminLocation(Base):
    __tablename__ = 'workspace_admin_locations'
    
    workspace_id: Mapped[int] = mapped_column(
        ForeignKey('workspace.id', ondelete='CASCADE'), 
        nullable=False,
        index=True,
        unique=True
    )
    
    state_id: Mapped[int] = mapped_column(Integer, nullable=False)
    district_ids: Mapped[list[int]] = mapped_column(ARRAY(Integer), nullable=False)
    subdistrict_ids: Mapped[Optional[list[int]]] = mapped_column(ARRAY(Integer), nullable=True)
    admin_storage: Mapped["UserDataStorage"] = relationship(
    back_populates="admin_shp",
    cascade="all, delete-orphan",
    single_parent=True,
    uselist=False
    )
    workspace: Mapped["Workspace"] = relationship(back_populates="admin_location")
    user_storage_id: Mapped[str] = mapped_column(
        ForeignKey("user_data_storage.unq_name", ondelete="CASCADE"),
        nullable=False,
        unique=True
    )

class WorkspaceDrainLocation(Base):
    __tablename__ = 'workspace_drain_locations'
    
    workspace_id: Mapped[int] = mapped_column(
        ForeignKey('workspace.id', ondelete='CASCADE'), 
        nullable=False,
        index=True,
        unique=True
    )
    river_ids: Mapped[list[int]] = mapped_column(ARRAY(Integer), nullable=False)
    village_ids:Mapped[list[int]] = mapped_column(ARRAY(Integer), nullable=False)
    drain_storage: Mapped["UserDataStorage"] = relationship(
    back_populates="drain_shp",
    cascade="all, delete-orphan",
    single_parent=True,
    uselist=False
    )
    workspace: Mapped["Workspace"] = relationship(back_populates="drain_location")
    drain_storage_id: Mapped[str] = mapped_column(
        ForeignKey("user_data_storage.unq_name", ondelete="CASCADE"),
        nullable=False,
        unique=True
    )


class WorkspaceModule(Base):
    __tablename__ = 'workspace_modules'
    workspace_id: Mapped[int] = mapped_column(
        ForeignKey("workspace.id", ondelete="CASCADE"),
        primary_key=True
    )

    module_id: Mapped[int] = mapped_column(
        ForeignKey("modules.id", ondelete="CASCADE"),
        primary_key=True
    )

    workspace: Mapped["Workspace"] = relationship(back_populates="workspace_modules")
    module: Mapped["Module"] = relationship(back_populates="workspace_modules")



    
class Workspace(Base):
    __tablename__ = "workspace"
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    location_type: Mapped[str] = mapped_column(String(50), nullable=False)  # drain or admin or custom 
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")
    workspace_modules: Mapped[list["WorkspaceModule"]] = relationship(
    back_populates="workspace",
    cascade="all, delete-orphan"
    )
    user: Mapped["User"] = relationship(back_populates="workspaces")
    admin_location: Mapped[Optional["WorkspaceAdminLocation"]] = relationship(
        back_populates="workspace", 
        cascade="all, delete-orphan", uselist=False
    )
    drain_location: Mapped[Optional["WorkspaceDrainLocation"]] = relationship(
        back_populates="workspace", 
        cascade="all, delete-orphan", uselist=False
    )
    workspacelayers: Mapped[List["WorkspaceLayers"]]=relationship(back_populates="workspace", cascade="all, delete-orphan")
    user_project: Mapped[List["Project"]] = relationship(back_populates="workspace", cascade="all, delete-orphan")



class WorkspaceLayers(Base):
    __tablename__ = "workspace_layer"
    workspace_id: Mapped[int] = mapped_column(
        ForeignKey('workspace.id', ondelete='CASCADE'), 
        nullable=False,
        index=True,
    )
    workspace:Mapped["Workspace"]=relationship(back_populates="workspacelayers")
    module_layer_def_id: Mapped[int] = mapped_column(ForeignKey('module_layer_definitions.id'), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    geo_layer_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    layer_path: Mapped[str] = mapped_column(String, nullable=False)
    sld_path:Mapped[Optional[str]]=mapped_column(String,nullable=True)

    source_type: Mapped[str] = mapped_column(String(20), nullable=False, default="global") 
    module_layer_def: Mapped["ModuleLayerDefinition"] = relationship()
    __table_args__ = (UniqueConstraint('workspace_id', 'module_layer_def_id'),)
 
class Project(Base):
    __tablename__ = "user_projects"
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    workspace_id: Mapped[int] = mapped_column(
        ForeignKey('workspace.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    module_id: Mapped[int] = mapped_column(ForeignKey('modules.id'), nullable=False)
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey('user_projects.id'), nullable=True)
    report_id: Mapped[str] = mapped_column(String(200), nullable=True)
    workspace: Mapped["Workspace"] = relationship(back_populates="user_project")
    module: Mapped["Module"] = relationship()
    data: Mapped[Optional["ProjectData"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
        single_parent=True,
        uselist=False,
    )
    __table_args__ = (UniqueConstraint('workspace_id', 'module_id', "id"),)


class ProjectData(Base):
    __tablename__ = "project_data"
    project_id: Mapped[int] = mapped_column(
        ForeignKey('user_projects.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        unique=True,
    )
    district_ids: Mapped[Optional[list[int]]] = mapped_column(ARRAY(Integer), nullable=True)
    subdistrict_ids: Mapped[Optional[list[int]]] = mapped_column(ARRAY(Integer), nullable=True)
    village_ids: Mapped[Optional[list[int]]] = mapped_column(ARRAY(Integer), nullable=True)
    towns_ids: Mapped[Optional[list[int]]] = mapped_column(ARRAY(Integer), nullable=True)
    rivers_ids: Mapped[Optional[list[int]]] = mapped_column(ARRAY(Integer), nullable=True)
    analysis_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True, default=dict)
    layers: Mapped[list | None] = mapped_column(JSONB, nullable=True, default=list)
    result_layers: Mapped[dict | list | None] = mapped_column(JSONB, nullable=True, default=dict)
    project: Mapped["Project"] = relationship(back_populates="data")

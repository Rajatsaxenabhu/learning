from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.models import RasterMetadata, UserStorage, VectorMetadata
from app.database.crud.base.async_base import CrudBase
from app.api.schema.raster_operation import useroperSchema, rasterMetaSchame, vectorMetaSchema


class userstorecrud(CrudBase):
    def __init__(self, db: AsyncSession, Model=UserStorage):
        self.db = db
        self.Model = Model
        self.obj = None

    async def get_details(self, file_id: str):
        query = select(self.Model).filter(self.Model.file_id == file_id)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def create_details(self, payload: useroperSchema):
        return await self.create(payload.model_dump())


class rasterMetacrud(CrudBase):
    def __init__(self, db: AsyncSession, Model=RasterMetadata):
        self.db = db
        self.Model = Model
        self.obj = None

    async def get_details(self, file_id: str):
        query = select(self.Model).filter(self.Model.file_id == file_id)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def create_details(self, payload: rasterMetaSchame):
        return await self.create(payload.model_dump())


class vectorMetacrud(CrudBase):
    def __init__(self, db: AsyncSession, Model=VectorMetadata):
        self.db = db
        self.Model = Model
        self.obj = None

    async def get_details(self, file_id: str):
        query = select(self.Model).filter(self.Model.file_id == file_id)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def create_details(self, payload: vectorMetaSchema):
        return await self.create(payload.model_dump())

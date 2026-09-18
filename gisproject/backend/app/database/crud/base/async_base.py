from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
import sqlalchemy as sq
from sqlalchemy import select

class CrudBase:
    def __init__(self, db: AsyncSession, Model=None):
        self.db = db
        self.Model = Model
        self.obj = None

    async def _missing_obj(self, obj, _id: int = 0):
        if obj is None:
            raise HTTPException(
                status_code=404,
                detail=f"detail not found with id {_id}"
            )

    async def _pagination(self, db, query, all_data: bool = True, page: int = 1, page_size: int = 5):
        if all_data:
            result = await db.execute(query)
            return result.scalars().all()
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await db.execute(query)
        return result.scalars().all()

    async def get(self, id: int):
        query = select(self.Model).filter(self.Model.id == id)
        result = await self.db.execute(query)
        self.obj = result.scalars().first()
        await self._missing_obj(self.obj, id)
        return self.obj

    async def get_all(self, all_data: bool = True):
        query = select(self.Model).order_by(sq.desc(self.Model.modified_at))
        return await self._pagination(self.db, query, all_data)

    async def create(self, data: dict):
        obj = self.Model(**data)
        self.db.add(obj)
        return await self.commit(obj)

    async def __update_obj(self, obj, data: dict):
        await self._missing_obj(obj, data.get('id', 0))
        if 'id' in data:
            data.pop('id')
        for key, value in data.items():
            setattr(obj, key, value)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def update(self, data: dict):
        query = select(self.Model).filter(self.Model.id == data.get('id'))
        result = await self.db.execute(query)
        obj = result.scalars().first()
        return await self.__update_obj(obj, data)

    async def update_email(self, data: dict):
        query = select(self.Model).filter(self.Model.email == data.get('email'))
        result = await self.db.execute(query)
        obj = result.scalars().first()
        return await self.__update_obj(obj, data)

    async def __delete_obj(self, obj):
        await self._missing_obj(obj)
        if obj:
            await self.db.delete(obj)
            await self.db.commit()
            return True
        return False

    async def delete(self, id: int):
        obj = await self.get(id)
        return await self.__delete_obj(obj=obj)

    async def commit(self, obj):
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def update_many(self):
        pass

    async def create_many(self, obj: list):
        for i in obj:
            await self.create(i)
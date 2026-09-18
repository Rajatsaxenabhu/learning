from app.database.crud.base.async_base import CrudBase
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,update
import sqlalchemy as sq
from sqlalchemy.orm import selectinload
from app.api.schema.auth_schema import signup_input
from app.database.models.workspace import User, UserDetails,Signup_temp
from app.api.exception.exceptions import UserNotRegistered

class SignupTempCrud(CrudBase):
    def __init__(self, db: AsyncSession, Model=Signup_temp):
        self.db = db
        self.Model = Model
        self.obj = None

    async def temp_user(self,payload:dict):
        return await self.create(payload)
    
    async def get_user(self,uniqueId:str):
        query=select(self.Model).filter(self.Model.temp_id==uniqueId)
        result = await self.db.execute(query)
        return result.scalars().first()
    
    async def update_user(self,uniqueId:str,status:str="confirmed"):
        query=update(self.Model).where(self.Model.temp_id==uniqueId).values(status=status).returning(self.Model)
        result = await self.db.execute(query)
        return result.scalars().first()
    
class UserCrud(CrudBase):
    def __init__(self, db: AsyncSession, Model=User):
        self.db = db
        self.Model = Model
        self.obj = None
    

    async def get_all_user(self,all_data:bool=True):
        query = select(self.Model).options(selectinload(self.Model.details)).order_by(sq.desc(self.Model.modified_at))
        return await self._pagination(self.db, query, all_data)

    async def user_signup(self, payload: signup_input):
        return await self.create(payload.model_dump())

    async def validate_email(self, email: str):
        query = (
            select(self.Model)
            .options(selectinload(self.Model.details))
            .filter(self.Model.email == email)
        )
        result = await self.db.execute(query)
        return result.scalars().first()

    async def delete_email(self, email: str):
        obj = await self.validate_email(email)
        if obj is None:
            raise UserNotRegistered
        return await self.delete(obj.id)

    async def get_user(self, id: int):
        query = select(self.Model).filter(self.Model.id == id)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def updates(self, payload: dict):
        return await self.update(payload)


class UserDetailCrud(CrudBase):
    def __init__(self, db: AsyncSession, Model=UserDetails):
        self.db = db
        self.Model = Model
        self.obj = None

    async def get_user_details(self, id: int):
        query = select(self.Model).filter(self.Model.user_id == id)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def updates(self, payload: dict):
        return await self.update(payload)
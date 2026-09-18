from app.database.models import (
    States_location, 
    Districts_location, 
    Subdistricts_location, 
    Villages_location, 
    Towns_location, 
    Rivers_location, 
    Catchments_location,
    Stp_location,
    Drain_location
    )
from app.database.crud.base.async_base import CrudBase
from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sq
from sqlalchemy import func, select

class Stp_State_crud(CrudBase):

    def __init__(self, db: AsyncSession, Model=States_location):
        super().__init__(db, Model)
        self.obj = None

    async def get_states(self, all_data: bool = True):
        query = select(self.Model).order_by(self.Model.state.asc())
        return await self._pagination(self.db, query, all_data)


class Stp_District_crud(CrudBase):

    def __init__(self, db: AsyncSession, Model=Districts_location):
        super().__init__(db, Model)
        self.obj = None

    async def get_district(self, state_id: int, all_data: bool = True):
        query = select(self.Model).filter(
            self.Model.state_c == state_id
        ).order_by(sq.asc(self.Model.district))
        return await self._pagination(self.db, query, all_data)

    async def get_district_all(self, all_data: bool = True):
        query = select(self.Model).order_by(sq.asc(self.Model.district))
        return await self._pagination(self.db, query, all_data)


class Stp_SubDistrict_crud(CrudBase):

    def __init__(self, db: AsyncSession, Model=Subdistricts_location):
        super().__init__(db, Model)
        self.obj = None

    async def get_subdistrict(self, district: list, all_data: bool = True):
        query = select(self.Model).filter(
            self.Model.district_c.in_(district)
        ).order_by(sq.asc(self.Model.subdistrict))
        return await self._pagination(self.db, query, all_data)

    async def get_subdistrict_all(self, all_data: bool = True):
        query = select(self.Model).order_by(sq.asc(self.Model.subdistrict))
        return await self._pagination(self.db, query, all_data)


class Stp_Villages_crud(CrudBase):

    def __init__(self, db: AsyncSession, Model=Villages_location):
        super().__init__(db, Model)
        self.obj = None

    async def get_villages(self, sub_district: list, all_data: bool = True):
        query = select(self.Model).filter(
            self.Model.subdistrict_c.in_(sub_district)
        ).order_by(sq.asc(self.Model.village))
        return await self._pagination(self.db, query, all_data)

    async def get_villages_details(self, village_id: list, all_data: bool = True):
        query = select(self.Model).filter(
            self.Model.village_c.in_(village_id)
        ).order_by(sq.asc(self.Model.village))
        return await self._pagination(self.db, query, all_data)



class Stp_towns_crud(CrudBase):

    def __init__(self, db: AsyncSession, Model=Towns_location):
        super().__init__(db, Model)
        self.obj = None

    async def get_sum_elevation(self, town_id: list, all_data: bool = True):
        query = select(func.sum(self.Model.elevation)).filter(
            self.Model.id.in_(town_id)
        )
        result = await self.db.execute(query)
        return result.scalar()

    async def get_towns(self, subdistrict: list, all_data: bool = True):
        query = select(self.Model).filter(
            self.Model.subdis_cod.in_(subdistrict)
        ).order_by(sq.asc(self.Model.town_name))
        return await self._pagination(self.db, query, all_data)

    async def get_all_towns(self, all_data: bool = True):
        query = select(self.Model).order_by(sq.asc(self.Model.town_name))
        return await self._pagination(self.db, query, all_data)


class Stp_River_crud(CrudBase):

    def __init__(self, db: AsyncSession, Model=Rivers_location):
        super().__init__(db, Model)
        self.obj = None

    async def get_rivers(self, all_data: bool = True):
        query = select(self.Model)
        return await self._pagination(self.db, query, all_data)
    
    async def search_river(self,search:str=None,page:int=1):
        if search is None:
            query=select(self.Model)
        else:
            query=select(self.Model).where(self.Model.River_Name.ilike(f"{search}%"))
        return await self._pagination(self.db,query,all_data=False,page=page,page_size=30)
    
    async def river_names(self,code:list=None):
        query=select(self.Model).filter(self.Model.River_Code.in_(code))
        return await self._pagination(self.db,query,all_data=True)



class Stp_catchment_crud(CrudBase):

    def __init__(self, db: AsyncSession, Model=Catchments_location):
        super().__init__(db, Model)
        self.obj = None

    async def get_cachement(self, Drain_No: list = None, all_data: bool = True):
        query = select(self.Model).filter(self.Model.Drain_No.in_(Drain_No))
        return await self._pagination(self.db, query, all_data)

class Stp_drains_crud(CrudBase):

    def __init__(self, db: AsyncSession, Model=Drain_location):
        super().__init__(db, Model)
        self.obj = None

    async def get_details(self, Drain_No: list = None, all_data: bool = True):
        query = select(self.Model).filter(self.Model.Drain_No.in_(Drain_No))
        return await self._pagination(self.db, query, all_data)

    async def drain_discharges(self, Drain_No: list = None):
        query = select(func.sum(self.Model.Discharge)).filter(self.Model.Drain_No.in_(Drain_No))
        result = await self.db.execute(query)
        return result.scalar() or None


    
class Stp_details_crud(CrudBase):

    def __init__(self, db: AsyncSession, Model=Stp_location):
        super().__init__(db, Model)
        self.obj = None

    def stp_details(self, Stp_id: int, all_data: bool = True):
        query = select(self.Model).filter(self.Model.stp_code==Stp_id)
        return self._pagination(self.db, query,all_data)

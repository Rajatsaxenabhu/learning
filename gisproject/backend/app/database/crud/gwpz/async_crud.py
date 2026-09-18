from sqlalchemy import and_, select

from app.database.crud.base.async_base import CrudBase
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import WaterQualityAssessment,GWQI_Threshold


class WQI(CrudBase):
    def __init__(self,db: AsyncSession,Model=WaterQualityAssessment):
        super().__init__(db,Model)
        self.obj = None
    
    async def get_wqi(self,subdis_code:list,year:int,all_data:bool=True):
        query = select(self.Model).filter(and_(self.Model.Year == year,self.Model.subdis_code.in_(subdis_code)))
        return await self._pagination(self.db, query, all_data)
    
    async def get_wqi_vill(self,village_code:list,year:int,all_data:bool=True):
        query = select(self.Model).filter(and_(self.Model.Year == year,self.Model.village_code.in_(village_code)))
        return await self._pagination(self.db, query, all_data)
    
    


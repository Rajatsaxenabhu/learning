from app.database.models import States_location,Districts_location,Subdistricts_location,Villages_location,Towns_location,Rivers_location,Catchments_location
from app.database.crud.base.sync_base import CrudBase
from sqlalchemy.orm import Session
import sqlalchemy as sq
from sqlalchemy import func
class Stp_State_crud(CrudBase):
    def __init__(self,db:Session,Model=States_location):
        super().__init__(db,Model)
        self.obj = None
    
    def get_states(self,all_data:bool=True,page=1, page_size=5):
        query= self.db.query(self.Model).filter().order_by(
            sq.asc(self.Model.state))
        return self._pagination(query,all_data,page,page_size)

class Stp_District_crud(CrudBase):
    def __init__(self,db:Session,Model=Districts_location):
        super().__init__(db,Model)
        self.obj = None

    def get_district(self,state_id:int,all_data:bool=True):
        query=self.db.query(self.Model).filter(
            self.Model.state_c==state_id).order_by( sq.asc(self.Model.district))
        return self._pagination(query,True)

    def get_district_all(self,all_data:bool=True,page=1, page_size=5):
        query=self.db.query(self.Model).order_by( sq.asc(self.Model.district))
        return self._pagination(query,all_data,page,page_size)

class Stp_SubDistrict_crud(CrudBase):
    def __init__(self,db:Session,Model=Subdistricts_location):
        super().__init__(db,Model)
        self.obj = None

    def get_subdistrict(self,district:list,all_data:bool=True):
        query=self.db.query(self.Model).filter(
            self.Model.district_c.in_(district)).order_by(sq.asc(self.Model.subdistrict))
        return self._pagination(query,all_data)
    
    def get_subdistrict_all(self,all_data:bool=True,page=1, page_size=5):
        query=self.db.query(self.Model).order_by( sq.asc(self.Model.subdistrict))
        return self._pagination(query,all_data,page,page_size)

class Stp_Villages_crud(CrudBase):
    def __init__(self,db:Session,Model=Villages_location):
        super().__init__(db,Model)
        self.obj = None

    def get_villages(self,sub_district:list,all_data:bool=True):
        query=self.db.query(self.Model).filter(
            self.Model.subdistrict_c.in_(sub_district)).order_by(sq.asc(self.Model.village))
        return self._pagination(query,all_data)

class Stp_towns_crud(CrudBase):
    def __init__(self,db:Session,Model=Towns_location):
        super().__init__(db,Model)
        self.obj = None

    def get_sum_elevation(self,town_id:list,all_data:bool=True):
        query = self.db.query(func.sum(self.Model.elevation)).filter(
        self.Model.id.in_(town_id))
        total_elevation = query.scalar() 
        return total_elevation
        
    def get_towns(self,subdistrict:list,all_data:bool=True):
        query=self.db.query(self.Model).filter(
            self.Model.subdistrict_code.in_(subdistrict)).order_by(sq.asc(self.Model.name))
        return self._pagination(query,all_data)

    def get_all_towns(self,all_data:bool=True):
        query=self.db.query(self.Model).order_by(sq.asc(self.Model.name))
        return self._pagination(query,all_data)
class Stp_River_crud(CrudBase):
    def __init__(self,db:Session,Model=Rivers_location):
        super().__init__(db,Model)
        self.obj = None

    def get_rivers(self,all_data:bool=True):
        query=self.db.query(self.Model).filter()
        return self._pagination(query,all_data)

    
class Stp_catchment_crud(CrudBase):
    def __init__(self,db:Session,Model=Catchments_location):
        super().__init__(db,Model)
        self.obj = None

    def get_cachement(self,Drain_No:list=None,all_data:bool=True):
        query=self.db.query(self.Model).filter(self.Model.Drain_No.in_(Drain_No))
        return self._pagination(query,all_data)
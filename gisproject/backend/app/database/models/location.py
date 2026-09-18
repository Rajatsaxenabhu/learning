from app.database.models.base import Base
from sqlalchemy.orm import Mapped,mapped_column, relationship
from sqlalchemy import ARRAY, Integer, String, Float,ForeignKey,Text
from typing import List


class States_location(Base):
    __tablename__ = "states_location"
    state_c: Mapped[int] = mapped_column(Integer,unique=True,nullable=False)
    state: Mapped[str] = mapped_column(String, nullable=False)
    districts: Mapped[List["Districts_location"]] = relationship(back_populates="state")

class Districts_location(Base):
    __tablename__ = "districts_location"

    district_c: Mapped[int] = mapped_column(Integer,unique=True,nullable=False)
    district: Mapped[str] = mapped_column(String, nullable=False)
    state_c: Mapped[int] = mapped_column(ForeignKey("states_location.state_c"), nullable=False, index=True)
    state: Mapped["States_location"] = relationship(back_populates="districts")
    subdistricts: Mapped[List["Subdistricts_location"]] = relationship(back_populates="district")

class Subdistricts_location(Base):
    __tablename__ = "subdistricts_location"
    subdistrict_c: Mapped[int] = mapped_column(Integer,unique=True,nullable=False)
    subdistrict: Mapped[str] = mapped_column(String, nullable=False)
    district_c: Mapped[int] = mapped_column(ForeignKey("districts_location.district_c"), nullable=False)
    district: Mapped["Districts_location"] = relationship(back_populates="subdistricts")
    towns:Mapped[List["Towns_location"]]= relationship(back_populates='subdistrict')
    villages:Mapped[List["Villages_location"]]= relationship(back_populates='subdistrict')

class Villages_location(Base):
    __tablename__="villages_location"
    village_c: Mapped[int] = mapped_column(Integer,unique=True,nullable=False)
    village:Mapped[str] = mapped_column(String, nullable=False)
    subdistrict_c: Mapped[int] = mapped_column(ForeignKey("subdistricts_location.subdistrict_c"), nullable=False)
    subdistrict: Mapped["Subdistricts_location"] = relationship(back_populates="villages")
    population: Mapped[int] = mapped_column(Integer,nullable=True)

    
class Towns_location(Base):
    __tablename__ = "towns_location"
    town_name: Mapped[str] = mapped_column(String, nullable=False)
    town_code: Mapped[int] = mapped_column(Integer, unique=True,nullable=False)
    classs: Mapped[int] = mapped_column(Integer,  nullable=False)
    total_popu: Mapped[int] = mapped_column(Integer, nullable=False)
    elevation: Mapped[float] = mapped_column(Float, nullable=False)
    subdis_cod: Mapped[int] = mapped_column(ForeignKey("subdistricts_location.subdistrict_c"), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    subdistrict: Mapped["Subdistricts_location"] = relationship(back_populates="towns")


class Rivers_location(Base):
    __tablename__ = "rivers_location"
    River_Code: Mapped[int] = mapped_column(Integer, unique=True,nullable=False)
    River_Name: Mapped[str] = mapped_column(String, nullable=False)
    drains: Mapped[List["Drain_location"]] = relationship(back_populates="river")
    catchments: Mapped[List["Catchments_location"]] = relationship(back_populates="river")


class Drain_location(Base):
    __tablename__ = "drains_location"
    Name: Mapped[str] = mapped_column(String, nullable=False)
    River_Code: Mapped[int] = mapped_column(ForeignKey("rivers_location.River_Code"), nullable=False, index=True)
    Discharge: Mapped[float] = mapped_column(Float, nullable=False)
    elevation: Mapped[float] = mapped_column(Float, nullable=False)
    Drain_No: Mapped[int] = mapped_column(Integer, unique=True,nullable=False)
    River_name: Mapped[str] = mapped_column(String, nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    river: Mapped["Rivers_location"] = relationship(back_populates="drains")
    Tapping_st: Mapped[str] = mapped_column(String, nullable=False)



class Catchments_location(Base):
    __tablename__ = "catchments_location"
    catch_code: Mapped[int] = mapped_column(Integer, nullable=False)
    river_code: Mapped[int] = mapped_column(ForeignKey("rivers_location.River_Code"), nullable=False, index=True)
    river: Mapped["Rivers_location"] = relationship(back_populates="catchments")


class Stp_location(Base):
    __tablename__ = "stp_location"
    stp_code: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    stp_name: Mapped[str] = mapped_column(String, nullable=False)
    stp_status: Mapped[str] = mapped_column(String, nullable=True)
    stp_mainta: Mapped[str] = mapped_column(String, nullable=True)
    stp_type: Mapped[str] = mapped_column(String, nullable=True)
    bod_actual: Mapped[float] = mapped_column(Float, nullable=True)
    bod_design: Mapped[float] = mapped_column(Float, nullable=True)
    cod_actual: Mapped[float] = mapped_column(Float, nullable=True)
    cod_design: Mapped[float] = mapped_column(Float, nullable=True)
    tss_actual: Mapped[float] = mapped_column(Float, nullable=True)
    tss_design: Mapped[float] = mapped_column(Float, nullable=True)
    ph_actual: Mapped[float] = mapped_column(Float, nullable=True)
    ph_design: Mapped[float] = mapped_column(Float, nullable=True)
    fc_actual: Mapped[float] = mapped_column(Float, nullable=True)
    fc_design: Mapped[float] = mapped_column(Float, nullable=True)
    capacity: Mapped[float] = mapped_column(Float, nullable=True)
    utilize: Mapped[float] = mapped_column(Float, nullable=True)
    tapped_dra: Mapped[str] = mapped_column(Text, nullable=True)
    river_name: Mapped[str] = mapped_column(String, nullable=True)
    district: Mapped[str] = mapped_column(String, nullable=True)
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    long: Mapped[float] = mapped_column(Float, nullable=False)



from app.database.models.base import Base
from sqlalchemy.orm import Mapped,mapped_column, relationship
from sqlalchemy import  Integer, String, Float
class WaterQualityAssessment(Base):
    __tablename__='water_quality_assessment'
    Location:Mapped[str]=mapped_column(String,nullable=False)
    Longitude:Mapped[float]=mapped_column(Float,nullable=False)
    Latitude:Mapped[float]=mapped_column(Float,nullable=False)
    pH_Level:Mapped[float]=mapped_column(Float,nullable=False)
    Electrical_Conductivity:Mapped[float]=mapped_column(Float,nullable=False)
    Carbonate:Mapped[float]=mapped_column( Float,nullable=False)
    Bicarbonate:Mapped[float]=mapped_column(Float,nullable=False)
    Chloride:Mapped[float]=mapped_column(Float,nullable=False)
    Fluoride:Mapped[float]=mapped_column(Float,nullable=False)
    Sulfate:Mapped[float]=mapped_column(Float,nullable=False)
    Nitrate:Mapped[float]=mapped_column(Float,nullable=False)
    Hardness:Mapped[float]=mapped_column(Float,nullable=False)
    Calcium:Mapped[float]=mapped_column(Float,nullable=False)
    Magnesium:Mapped[float]=mapped_column(Float,nullable=False)
    Sodium:Mapped[float]=mapped_column(Float,nullable=False)
    Potassium:Mapped[float]=mapped_column(Float,nullable=False)
    Iron:Mapped[float]=mapped_column(Float,nullable=False)
    Arsenic:Mapped[float]=mapped_column(Float,nullable=False)
    Uranium:Mapped[float]=mapped_column(Float,nullable=False)
    village_code:Mapped[int]=mapped_column(Integer,nullable=False)
    subdis_code:Mapped[int]=mapped_column(Integer,nullable=False)
    Year:Mapped[int]=mapped_column(Integer,nullable=False)

class GWQI_Threshold(Base):
    __tablename__='GWQI_param_Index'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    parameter:Mapped[str]=mapped_column(String,nullable=False)
    value:Mapped[float]=mapped_column(Float,nullable=False)
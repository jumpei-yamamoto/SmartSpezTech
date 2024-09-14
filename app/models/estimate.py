from sqlalchemy import Column, Integer, String, Text
from app.database import Base  # Baseはdatabase.pyで宣言したdeclarative_base()

class Estimate(Base):
    __tablename__ = 'estimate_data'  # テーブル名

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, index=True)
    inquiry = Column(Text)
    requirements_specification = Column(Text)
    requirements_definition = Column(Text)
    screens = Column(Text)
    estimate_develop = Column(Text)
    analysis = Column(Text)

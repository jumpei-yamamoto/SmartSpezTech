from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum, JSON, Float
from sqlalchemy.orm import relationship
from app.database import Base  # Baseはdatabase.pyで宣言したdeclarative_base()
from enum import IntEnum
from sqlalchemy.dialects.postgresql import ARRAY

class EstimateStatus(IntEnum):
    PENDING = 0
    ACCEPTED = 1
    ORDERED = 2
    COMPLETED = 3   
    CANCELLED = 4

class Estimate(Base):
    __tablename__ = 'estimate_data'  # テーブル名

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, index=True)
    inquiry = Column(Text)
    answers = Column(Text)
    status = Column(Integer, default=EstimateStatus.PENDING, nullable=False)  # Integer 型を使用

    # 画面情報との関連付け
    screens = relationship("Screen", back_populates="estimate")

    events = relationship("Event", back_populates="estimate")
    entities = relationship("Entity", back_populates="estimate")
    relations = relationship("Relation", back_populates="estimate")
    ai_response = relationship("AIResponse", back_populates="estimate", uselist=False)

class Screen(Base):
    __tablename__ = 'screen_data'

    id = Column(Integer, primary_key=True, index=True)
    estimate_id = Column(Integer, ForeignKey('estimate_data.id'))
    title = Column(String)
    catchphrase = Column(String)
    description = Column(Text)
    preview = Column(Text)

    # Estimateとの関連付け
    estimate = relationship("Estimate", back_populates="screens")

class Event(Base):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True, index=True)
    estimate_id = Column(Integer, ForeignKey('estimate_data.id'))
    name = Column(String)
    screen = Column(String)
    process = Column(Text)

    estimate = relationship("Estimate", back_populates="events")

class Entity(Base):
    __tablename__ = 'entities'

    id = Column(Integer, primary_key=True, index=True)
    estimate_id = Column(Integer, ForeignKey('estimate_data.id'))
    name = Column(String)
    attributes = Column(JSON)

    estimate = relationship("Estimate", back_populates="entities")

class Relation(Base):
    __tablename__ = 'relations'

    id = Column(Integer, primary_key=True, index=True)
    estimate_id = Column(Integer, ForeignKey('estimate_data.id'))
    from_ = Column(String)
    to = Column(String)
    type = Column(String)

    estimate = relationship("Estimate", back_populates="relations")

class AIResponse(Base):
    __tablename__ = "ai_responses"

    id = Column(Integer, primary_key=True, index=True)
    estimate_id = Column(Integer, ForeignKey("estimate_data.id"))
    screens = Column(JSON)
    events = Column(JSON)
    database = Column(JSON)

    estimate = relationship("Estimate", back_populates="ai_response")



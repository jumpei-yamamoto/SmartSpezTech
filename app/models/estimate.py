from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.database import Base  # Baseはdatabase.pyで宣言したdeclarative_base()
import enum

class EstimateStatus(enum.Enum):
    PENDING = 0
    ACCEPTED = 1
    CANCELLED = 2

class Estimate(Base):
    __tablename__ = 'estimate_data'  # テーブル名

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, index=True)
    inquiry = Column(Text)
    answers = Column(Text)
    status = Column(Enum(EstimateStatus), default=EstimateStatus.PENDING, nullable=False)

    # 画面情報との関連付け
    screens = relationship("Screen", back_populates="estimate")

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


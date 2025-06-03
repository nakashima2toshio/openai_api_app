# sample_table サンプル
"""
2. テーブル設計
テーブル名: items
--------------------------------------
カラム名	    型	        説明
--------------------------------------
id	        int	主キー
name	    varchar	    アイテム名
description	varchar	    説明
price	    int	        価格
status	    varchar	    ステータス
created_at	datetime	作成日時
updated_at	datetime	更新日時
"""
# db_models.py
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime
from pydantic import BaseModel

Base = declarative_base()

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Integer, nullable=False)
    status = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Pydantic スキーマ
class ItemCreate(BaseModel):
    name: str
    description: str | None = None
    price: int
    status: str | None = None

class ItemRead(BaseModel):
    id: int
    name: str
    description: str | None = None
    price: int
    status: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

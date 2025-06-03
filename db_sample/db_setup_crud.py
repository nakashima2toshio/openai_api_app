# db_setup
# main.py
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
from db_models import Base, Item, ItemCreate, ItemRead
from datetime import datetime

DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

# テーブル作成
Base.metadata.create_all(bind=engine)

def create_item(db: Session, item: ItemCreate) -> ItemRead:
    now = datetime.utcnow()
    db_item = Item(
        name=item.name,
        description=item.description,
        price=item.price,
        status=item.status,
        created_at=now,
        updated_at=now
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return ItemRead.from_orm(db_item)

def get_item(db: Session, item_id: int) -> ItemRead | None:
    item = db.query(Item).filter(Item.id == item_id).first()
    if item:
        return ItemRead.from_orm(item)
    return None

if __name__ == "__main__":
    db = SessionLocal()
    item_in = ItemCreate(name="サンプル商品", description="説明文", price=1500, status="active")
    item_out = create_item(db, item_in)
    print("登録結果:", item_out)

    get_item_out = get_item(db, item_out.id)
    print("取得結果:", get_item_out)

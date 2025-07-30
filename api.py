
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from db import SessionLocal, engine
from models import Base, Ad


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Divar Property API",
    description="API for accessing crawled Divar property data."
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class AdResponse(BaseModel):
    id: int
    link: str
    title: str
    publish_date: Optional[str] = None
    area: Optional[str] = None
    price: Optional[str] = None
    description: Optional[str] = None
    num_rooms: Optional[str] = None
    meterage: Optional[str] = None
    year_built: Optional[str] = None
    crawled_at: datetime

    class Config:
        orm_mode = True


@app.get("/ads/", response_model=List[AdResponse], summary="Retrieve a list of all ads")
def read_ads(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    ads = db.query(Ad).offset(skip).limit(limit).all()
    return ads

# جزئیات آگهی با شناسه
@app.get("/ads/{ad_id}", response_model=AdResponse, summary="Retrieve details of a specific ad by ID")
def read_ad(ad_id: int, db: Session = Depends(get_db)):
    ad = db.query(Ad).filter(Ad.id == ad_id).first()
    if ad is None:
        raise HTTPException(status_code=404, detail="Ad not found")
    return ad

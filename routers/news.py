from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path, UploadFile, File, Form
from starlette import status
from pydantic import BaseModel, Field

from database import SessionLocal
from models import News

router = APIRouter(
    prefix='/news',
    tags=['news']
)


class NewsRequest(BaseModel):
    title_uz: Annotated[str, Form()]
    title_ru: Annotated[str, Form()]
    image: UploadFile = None
    is_active: Annotated[bool, Form()]
    description_uz: Annotated[str, Form()]
    description_ru: Annotated[str, Form()]
    detail_image: UploadFile = None


def get_db():
    db = SessionLocal()
    try:
        yield db

    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@router.get('/', status_code=status.HTTP_200_OK)
async def get_all_news(db: db_dependency):
    result = db.query(News).all()
    if result:
        return result

    raise HTTPException(status_code=404, detail='News not found.')


@router.get('/{news_id}', status_code=status.HTTP_200_OK)
async def get_current_news(news_id: int, db: db_dependency):
    current_product = db.query(News).filter(News.id == news_id).first()
    if current_product:
        return current_product

    raise HTTPException(status_code=404, detail='News not found.')


@router.post('/add-news', status_code=status.HTTP_201_CREATED)
async def add_news(db: db_dependency, news_request: NewsRequest = Depends(NewsRequest)):
    news_model = News(
        title_uz=news_request.title_uz,
        title_ru=news_request.title_ru,
        image=news_request.image.filename,
        is_active=news_request.is_active,
        description_uz=news_request.description_uz,
        description_ru=news_request.description_ru,
        detail_image=news_request.detail_image.filename
    )

    db.add(news_model)
    db.commit()

    return status.HTTP_201_CREATED


@router.put('/update-new/{new_id}', status_code=status.HTTP_204_NO_CONTENT)
async def update_new(new_id: int, db: db_dependency,
                     news_request: NewsRequest = Depends(NewsRequest)):
    news_model = db.query(News).filter(News.id == new_id).first()

    if news_model is None:
        raise HTTPException(status_code=404, detail='News not found.')

    news_model.title_uz = news_request.title_uz
    news_model.title_ru = news_request.title_ru
    news_model.image = news_request.image.filename
    news_model.is_active = news_request.is_active
    news_model.description_uz = news_request.description_uz
    news_model.description_ru = news_request.description_ru
    news_model.detail_image = news_request.detail_image.filename

    db.add(news_model)
    db.commit()


@router.delete('/delete-new/{new_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_new(new_id: int, db: db_dependency):
    new_to_delete = db.query(News).filter(News.id == new_id).first()

    if new_to_delete is None:
        raise HTTPException(status_code=404, detail='New not found.')

    db.query(News).filter(News.id == new_id).first().delete()
    db.commit()

from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path, UploadFile, File, Form
from starlette import status
from pydantic import BaseModel, Field

from database import SessionLocal
from models import Product

router = APIRouter(
    prefix='/product',
    tags=['products']
)


class ProductRequest(BaseModel):
    name: str
    image: UploadFile = None
    price: int
    display_order: int
    remaining_quantity: int
    is_active: bool
    filial: str


def get_db():
    db = SessionLocal()
    try:
        yield db

    finally:
        db.close()


@router.get('/', status_code=status.HTTP_200_OK)
async def get_all_products(db: Session = Depends(get_db)):
    result = db.query(Product).all()
    if result:
        return result

    raise HTTPException(status_code=404, detail='Products not found.')


@router.get('/{product_id}', status_code=status.HTTP_200_OK)
async def get_current_products(product_id: int, db: Session = Depends(get_db)):
    current_product = db.query(Product).filter(Product.id == product_id).first()
    if current_product:
        return current_product

    raise HTTPException(status_code=404, detail='Products not found.')


@router.post('/add-product', status_code=status.HTTP_201_CREATED)
async def add_product(db: Session = Depends(get_db), product_request: ProductRequest = Depends(ProductRequest)):

    product_model = Product(name=product_request.name,
                            image=product_request.image.filename,
                            price=product_request.price,
                            display_order=product_request.display_order,
                            remaining_quantity=product_request.remaining_quantity,
                            is_active=product_request.is_active,
                            filial=product_request.filial)
    db.add(product_model)
    db.commit()


@router.put('/update-product/{product_id}', status_code=status.HTTP_204_NO_CONTENT)
async def update_product(product_id: int, db: Session = Depends(get_db),
                         product_request: ProductRequest = Depends(ProductRequest)):

    product_model = db.query(Product).filter(Product.id == product_id).first()

    if product_model is None:
        raise HTTPException(status_code=404, detail='Product not found.')

    product_model.name = product_request.name
    product_model.image = product_request.image.filename
    product_model.price = product_request.price
    product_model.display_order = product_request.display_order
    product_model.remaining_quantity = product_request.remaining_quantity
    product_model.is_active = product_request.is_active
    product_model.filial = product_request.filial

    db.add(product_model)
    db.commit()


@router.delete('/delete-product/{product_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    product_model = db.query(Product).filter(Product.id == product_id).first()
    if product_model is None:
        raise HTTPException(status_code=404, detail='Product not found.')

    db.query(Product).filter(Product.id == product_id).delete()
    db.commit()

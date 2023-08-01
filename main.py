from fastapi import FastAPI
import models
from database import engine
from routers import product, news, messages

models.Base.metadata.create_all(bind=engine)


app = FastAPI()

app.include_router(product.router)
app.include_router(news.router)
app.include_router(messages.router)


@app.get('/')
async def main():
    return {'message': 'Hello from MARS!'}

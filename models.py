from database import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, func


# таблица для продуктов
class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    image = Column(String)
    price = Column(Integer, nullable=False)
    display_order = Column(Integer, nullable=False)
    remaining_quantity = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    filial = Column(String, nullable=False)


# таблица новости
class News(Base):
    __tablename__ = 'news'

    id = Column(Integer, primary_key=True, index=True)
    title_uz = Column(String, nullable=False)
    title_ru = Column(String, nullable=False)
    image = Column(String)
    created_datetime = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True, nullable=False)
    description_uz = Column(Text, nullable=False)
    description_ru = Column(Text, nullable=False)
    detail_image = Column(String, nullable=True)


# таблица отправки сообшении
class SendingMessage(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    start_sending = Column(DateTime, nullable=False)
    end_sending = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    video_tg_file_id = Column(String, nullable=True)

    video1 = Column(String, nullable=True)
    image1 = Column(String, nullable=True)

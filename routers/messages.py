from typing import Annotated, Optional
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path, UploadFile, File, Form
from starlette import status
from pydantic import BaseModel, Field

from datetime import datetime

from starlette.background import BackgroundTasks

from database import SessionLocal
from models import SendingMessage

import smtplib
from email.message import EmailMessage

from celery import Celery

router = APIRouter(
    prefix='/messages',
    tags=['messages']
)


def get_db():
    db = SessionLocal()
    try:
        yield db

    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

SMTP_HOST = 'smtp.gmail.com'
SMTP_PORT = 465

celery = Celery('tasks', broker='redis://localhost:6379')


# sending gmail (not finished 100% but working)
def get_email_template_dashboard(username: str, db):
    form = db.query(SendingMessage).all()
    email = EmailMessage()
    email['Subject'] = 'Сообщения'
    email['From'] = 'bakhodyrov17@gmail.com'
    email['To'] = 'YOUR GMAIL'  # don't forget to input your gmail!
    email.set_content(
        f'Здравствуйте, {username}!'
        f'{form[1].text}\n'
    )

    return email


# celery task
# @celery.tasks
def send_email_report_dashboard(username: str, db):
    email = get_email_template_dashboard(username, db)
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
        server.login('bakhodyrov17@gmail.com', 'ngsxjidcprsfgwpi')
        server.send_message(email)


class MessageRequest(BaseModel):
    text: Annotated[str, Form()]
    start_sending: Annotated[datetime, Form()] = datetime.utcnow()
    end_sending: Annotated[datetime, Form()] = datetime.utcnow()
    notes: Annotated[str, Form()]
    video_tg_file_id: Optional[Annotated[str, Form()]]
    video1: UploadFile = None
    image1: UploadFile = None


class User(BaseModel):
    username: str = 'MARS'


# sending email with background tasks or celery
@router.get('/send-messages', status_code=status.HTTP_200_OK)
async def get_dashboard(background_tasks: BackgroundTasks, db: db_dependency, user=Depends(User)):
    background_tasks.add_task(send_email_report_dashboard, user.username, db)
    # send_email_report_dashboard(user.username)  # for celery

    return {'status': status.HTTP_200_OK, 'data': 'Сообщение отправилено'}


# start restefull api of messages
@router.get('/', status_code=status.HTTP_200_OK)
async def get_all_messages(db: db_dependency):
    result = db.query(SendingMessage).all()
    if result:
        return result

    raise HTTPException(status_code=404, detail='Message not found.')


@router.post('/add-message', status_code=status.HTTP_201_CREATED)
async def add_message(db: db_dependency, message_request: MessageRequest = Depends(MessageRequest)):
    message_model = SendingMessage(
        text=message_request.text,
        start_sending=message_request.start_sending,
        end_sending=message_request.end_sending,
        notes=message_request.notes,
        video_tg_file_id=message_request.video_tg_file_id,
        video1=message_request.video1.filename,
        image1=message_request.image1.filename
    )

    db.add(message_model)
    db.commit()


@router.put('/update-message/{message_id}', status_code=status.HTTP_204_NO_CONTENT)
async def update_new(message_id: int, db: db_dependency,
                     message_request: MessageRequest = Depends(MessageRequest)):
    message_model = db.query(SendingMessage).filter(SendingMessage.id == message_id).first()

    if message_model is None:
        raise HTTPException(status_code=404, detail='Message not found.')

    message_model.text = message_request.text
    message_model.start_sending = message_request.start_sending
    message_model.end_sending = message_request.end_sending
    message_model.notes = message_request.notes
    message_model.video_tg_file_id = message_request.video_tg_file_id
    message_model.video1 = message_request.video1.filename,
    message_model.image1 = message_request.image1.filename,

    db.add(message_model)
    db.commit()


@router.delete('/delete-message/{message_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_new(message_id: int, db: db_dependency):
    message_to_delete = db.query(SendingMessage).filter(SendingMessage.id == message_id).first()

    if message_to_delete is None:
        raise HTTPException(status_code=404, detail='Message not found.')

    db.query(SendingMessage).filter(SendingMessage.id == message_id).first().delete()
    db.commit()

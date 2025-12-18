import shutil

from fastapi import APIRouter, UploadFile

from app.tasks.tasks import process_pic

router = APIRouter(
    prefix='/images',
    tags=['upload image']
)

@router.post('/hotels')
async def add_hotel_images(name: int, file: UploadFile):
    im_path = f'app/static/image/{name}.webp'
    with open(im_path, 'wb+') as file_object:
        shutil.copyfileobj(file.file, file_object)
    process_pic.delay(im_path)
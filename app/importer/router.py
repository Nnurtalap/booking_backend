from fastapi import APIRouter, Depends, UploadFile
from app.users.dependencies import get_current_user
from typing import Literal
from app.importer.utils import TABLE_MODEL_MAP, convert_csv_to_postgres_format
import codecs
import csv
from app.exceptions import CannotAddDataToDatabase, CannotProcessCSV
from fastapi_versioning import version

router = APIRouter(
    prefix='/imports',
    tags=['Импорт данных в БД']
)

@router.post(
    '/{tablename}',
    
    status_code=201,
    dependencies=[Depends(get_current_user)]
)
@version(1)
async def import_data_to_table(
    file: UploadFile,
    table_name: Literal['hotels', 'booking', 'rooms']
):
    ModelDAO = TABLE_MODEL_MAP[table_name]
    csv_reader = csv.DictReader(codecs.iterdecode(file.file, 'utf-8'), delimiter=';')
    data = convert_csv_to_postgres_format(csv_reader)
    file.file.close()
    if not data:
        raise CannotProcessCSV
    added_data = await ModelDAO.add_bulk(data)
    if not added_data:
        raise CannotAddDataToDatabase


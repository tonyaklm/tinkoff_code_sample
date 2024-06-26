import httpx
from start_session import origination_get_session
from tables import Application
from common.Repository import repo
import json
from config import settings
from common.ApplicationStatus import ApplicationStatus
from http import HTTPStatus


async def update_status(application_id: int, new_status: str):
    """ Изменяет статус заявки по ее id"""

    async for orig_session in origination_get_session():
        await repo.update_item(Application, 'id', application_id, 'status', new_status, orig_session)


async def get_new_applications():
    """ Возвращает все заявки со статусом NEW"""

    async for orig_session in origination_get_session():
        return await repo.select_by_criteria(Application, ['status'], [ApplicationStatus.new.value], orig_session)


async def send_application_to_scoring(application: Application):
    """ Отправляет заявку в Scoring"""
    headers = {"Content-Type": "application/json"}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{settings.scoring_url}/",
                                         json=json.dumps(application.as_dict(), indent=4, sort_keys=True, default=str),
                                         headers=headers)
        except httpx.ConnectError:
            return False
        if response.status_code == HTTPStatus.OK:
            return True
    return False


async def scan_and_send_applications():
    new_applications = await get_new_applications()

    for application in new_applications:
        if await send_application_to_scoring(application):
            await update_status(application.id, ApplicationStatus.scoring.value)

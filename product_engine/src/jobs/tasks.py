import httpx
from start_session import pe_get_session
from tables import Agreement
from common.Repository import repo
from common.AgreementStatus import AgreementStatus
from config import settings
from http import HTTPStatus


async def send_application_again(agreement: Agreement):
    """ Досоздание заявки на кредит, отправляет в Origination создаваться"""

    agreement_data = {
        "agreement_id": agreement.id,
        "product_code": agreement.product_code
    }
    headers = {"Content-Type": "application/json"}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{settings.origination_url}/application/by/agreement",
                                         json=agreement_data, headers=headers)
        except httpx.ConnectError:
            return False
    return True


async def get_new_agreements():
    """ Возвращает все кредитные договоры со статусом NEW"""

    async for pe_session in pe_get_session():
        return await repo.select_by_criteria(Agreement, ['status'], [AgreementStatus.new.value], pe_session)


async def check_agreement_in_origination(agreement_id: int):
    """ Проверяет наличие заявки в Origination"""

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{settings.origination_url}/application/{agreement_id}")
        except httpx.ConnectError:
            return True
        if response.status_code == HTTPStatus.NOT_FOUND:
            return False
    return True


async def check_agreements():
    new_agreements = await get_new_agreements()

    for agreement in new_agreements:
        if not await check_agreement_in_origination(agreement.id):
            await send_application_again(agreement)

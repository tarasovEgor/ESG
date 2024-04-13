import requests

from common.schemes import (
    ApiBank,
    ApiMfo,
    PatchSource,
    Source,
    SourceRequest,
    TextRequest,
)
from common.settings import Settings
from utils.logger import get_logger

URL = Settings().api_url
logger = get_logger(__name__)


def get_bank_list() -> list[ApiBank]:
    url = URL + "/bank/"
    logger.debug(f"Get bank list from {url}")
    r = requests.get(url)
    banks = [ApiBank(**bank) for bank in r.json()["items"]]
    return banks


def get_insurance_list() -> list[ApiBank]:
    url = URL + "/bank/insurance"
    logger.debug(f"Get insurance list from {url}")
    r = requests.get(url)
    banks = [ApiBank(**bank) for bank in r.json()["items"]]
    return banks


def get_broker_list() -> list[ApiBank]:
    url = URL + "/bank/broker"
    logger.debug(f"Get broker list from {url}")
    r = requests.get(url)
    banks = [ApiBank(**bank) for bank in r.json()["items"]]
    return banks


def get_mfo_list() -> list[ApiMfo]:
    url = URL + "/bank/mfo"
    logger.debug(f"Get mfo list from {url}")
    r = requests.get(url)
    banks = [ApiMfo.from_api_bank(ApiBank(**bank)) for bank in r.json()["items"]]
    return banks


def send_source(source: SourceRequest) -> Source:
    url = URL + "/source/"
    logger.debug(f"Send source to {url}")
    r = requests.post(url, json=source.dict())
    if r.status_code != 200:
        logger.error(r.json())
        raise Exception("Error send source")
    return Source(**r.json())


def get_source_by_id(source_id: int) -> Source:
    url = URL + f"/source/item/{source_id}"
    logger.debug(f"Patch source {url}")
    r = requests.get(url)
    return Source(**r.json())


def patch_source(source_id: int, source: PatchSource) -> Source:
    data = source.dict()
    if data["last_update"]:
        data["last_update"] = data["last_update"].isoformat()
    url = URL + f"/source/item/{source_id}"
    logger.debug(f"Patch source {url}")
    r = requests.patch(url, json=data)
    if r.status_code != 200:
        logger.error(r.json())
        raise Exception("Error patch source")
    return Source(**r.json())


def send_texts(text: TextRequest) -> None:
    if len(text.items) == 0:
        return None
    items = []
    for item in text.items:
        d = item.dict()
        d["date"] = d["date"].isoformat()
        items.append(d)
    last_update = None
    if text.last_update:
        last_update = text.last_update.isoformat()
    request = {"items": items, "date": last_update, "parser_state": text.parsed_state}
    url = URL + "/text/"
    logger.debug(f"Send texts to {url}")
    r = requests.post(url, json=request)
    if r.status_code != 200:
        logger.error(r.json())
        raise Exception(r.json())

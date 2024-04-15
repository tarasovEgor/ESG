import requests
import json

from json.decoder import JSONDecodeError


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


# def send_source(source: SourceRequest) -> Source:
#     url = URL + "/source/"
#     logger.debug(f"Send source to {url}")
#     r = requests.post(url, json=source.dict()) #!!!
#     if r.status_code != 200:
#         logger.error(r.json())
#         raise Exception("Error send source")
#     return Source(**r.json())


def send_source(source: SourceRequest) -> Source:
    url = URL + "/source/"
    logger.debug(f"Send source to {url}")
    r = requests.post(url, json=source.dict())
    try:
        r.raise_for_status()  
        return Source(**r.json())
    except JSONDecodeError:
        logger.error("Failed to decode JSON from server response")
        return None  
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {e}")
        return None 



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
    try:
        r = requests.post(url, json=request)
        r.raise_for_status()
    except Exception as e:
        try:
            error_detail = r.json().get('detail')
            if error_detail == 'Source or bank not found':
                # raise SourceBankNotFoundError("Source or bank not found")
                error_message = "Source or bank not found"
                logger.error(error_message)
                return
            else:
                error_message = f"Error sending texts: {error_detail}" if error_detail is not None else "Error sending texts: Unexpected response format"
        except (json.JSONDecodeError, AttributeError):
            error_message = "Error sending texts: Unexpected response format"
        logger.error(error_message)
        return

class SourceBankNotFoundError(Exception):
    pass


# VER. 1

# def send_texts(text: TextRequest) -> None:
#     if len(text.items) == 0:
#         return None
#     items = []
#     for item in text.items:
#         d = item.dict()
#         d["date"] = d["date"].isoformat()
#         items.append(d)
#     last_update = None
#     if text.last_update:
#         last_update = text.last_update.isoformat()
#     request = {"items": items, "date": last_update, "parser_state": text.parsed_state}
#     url = URL + "/text/"
#     logger.debug(f"Send texts to {url}")
#     r = requests.post(url, json=request)
#     if r.status_code != 200:
#         try:
#             error_detail = r.json().get('detail')
#             if error_detail == 'Source or bank not found':
#                 raise SourceBankNotFoundError("Source or bank not found")
#             else:
#                 error_message = f"Error sending texts: {error_detail}" if error_detail is not None else "Error sending texts: Unexpected response format"
#         except json.JSONDecodeError:
#             error_message = f"Error sending texts: Unexpected response format"
#         logger.error(error_message)
#         raise Exception(error_message)

# class SourceBankNotFoundError(Exception):
#     pass


# VER. 0

# def send_texts(text: TextRequest) -> None:
#     if len(text.items) == 0:
#         return None
#     items = []
#     for item in text.items:
#         d = item.dict()
#         d["date"] = d["date"].isoformat()
#         items.append(d)
#     last_update = None
#     if text.last_update:
#         last_update = text.last_update.isoformat()
#     request = {"items": items, "date": last_update, "parser_state": text.parsed_state}
#     url = URL + "/text/"
#     logger.debug(f"Send texts to {url}")
#     r = requests.post(url, json=request)
#     if r.status_code != 200:
#         try:
#             error_detail = r.json().get('detail')
#             if error_detail == 'Source or bank not found':
#                 raise SourceBankNotFoundError("Source or bank not found")
#             else:
#                 error_message = f"Error sending texts: {error_detail}"
#         except json.JSONDecodeError:
#             error_message = f"Error sending texts: Unexpected response format"
#         logger.error(error_message)
#         raise Exception(error_message)

# class SourceBankNotFoundError(Exception):
#     pass

# INITIAL FUNC BELOW

# def send_texts(text: TextRequest) -> None:
#     if len(text.items) == 0:
#         return None
#     items = []
#     for item in text.items:
#         d = item.dict()
#         d["date"] = d["date"].isoformat()
#         items.append(d)
#     last_update = None
#     if text.last_update:
#         last_update = text.last_update.isoformat()
#     request = {"items": items, "date": last_update, "parser_state": text.parsed_state}
#     url = URL + "/text/"
#     logger.debug(f"Send texts to {url}")
#     r = requests.post(url, json=request)
#     if r.status_code != 200:
#         logger.error(r.json())
#         raise Exception(r.json())

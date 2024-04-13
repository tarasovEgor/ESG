from datetime import datetime

from common.api import (
    get_bank_list,
    get_broker_list,
    get_insurance_list,
    get_mfo_list,
    get_source_by_id,
    patch_source,
    send_source,
    send_texts,
)
from common.schemes import PatchSource, Source, SourceRequest, Text, TextRequest
from tests.utils import check_used_paths

response_source_mock = Source(
    id=1,
    site="test",
    source_type_id=1,
    parser_state='{"bank_id": 100, "page": 1}',
    last_update=datetime(2022, 1, 1, 0, 0),
)


def test_get_bank_list(mock_bank_list):
    banks = get_bank_list()
    assert len(banks) == 3
    assert mock_bank_list.call_count == 1
    assert check_used_paths(mock_bank_list, "GET", "/bank/") == 1


def test_get_insuarance_list(mock_insurance_list):
    insurances = get_insurance_list()
    assert len(insurances) == 3
    assert mock_insurance_list.call_count == 1
    assert check_used_paths(mock_insurance_list, "GET", "/bank/insurance") == 1


def test_get_broker_list(mock_broker_list):
    broker = get_broker_list()
    assert len(broker) == 3
    assert mock_broker_list.call_count == 1
    assert check_used_paths(mock_broker_list, "GET", "/bank/broker") == 1


def test_get_mfo_list(mock_mfo_list):
    mfo = get_mfo_list()
    assert len(mfo) == 3
    assert mock_mfo_list.call_count == 1
    assert check_used_paths(mock_mfo_list, "GET", "/bank/mfo") == 1


def test_send_source(mock_source):
    source = SourceRequest(site="test", source_type="test")
    source_response = send_source(source)
    assert mock_source.call_count == 1
    assert check_used_paths(mock_source, "POST", "/source/") == 1
    assert source_response == response_source_mock


def test_get_source_by_id(mock_get_source_by_id):
    source_id = 1
    source = get_source_by_id(source_id)
    assert mock_get_source_by_id.call_count == 1
    assert check_used_paths(mock_get_source_by_id, "GET", f"/source/item/{source_id}") == 1
    assert source == response_source_mock


def test_patch_source(mock_get_source_by_id):
    source_id = 1
    source_response = patch_source(source_id, PatchSource())
    assert mock_get_source_by_id.call_count == 1
    assert check_used_paths(mock_get_source_by_id, "PATCH", f"/source/item/{source_id}") == 1
    assert source_response == response_source_mock


def test_send_texts(mock_text):
    texts = TextRequest(
        items=[
            Text(
                source_id=1,
                text="test",
                title="test",
                link="test",
                date=datetime.now(),
                bank_id=1,
            )
        ]
    )
    send_texts(texts)
    assert mock_text.call_count == 1
    assert check_used_paths(mock_text, "POST", "/text/") == 1

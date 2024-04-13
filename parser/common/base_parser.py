import json
from abc import ABC
from datetime import datetime, timedelta

from common.schemes import Source
from common.settings import get_settings
from utils.logger import get_logger


class BaseParser(ABC):
    logger = get_logger(__name__, get_settings().logger_level)

    def parse(self) -> None:
        raise NotImplementedError

    def get_source_params(self, source: Source) -> tuple[int, int, datetime]:
        self.logger.debug(f"get source params {source=}")
        parsed_time = datetime.today() - timedelta(days=7)
        if parsed_time is None:
            parsed_time = datetime.fromtimestamp(1)
        parsed_time = parsed_time.replace(tzinfo=None)
        parsed_state = {}
        if source.parser_state is not None:
            parsed_state = json.loads(source.parser_state)
        parsed_bank_id = int(parsed_state.get("bank_id", "0"))
        parsed_bank_page = int(parsed_state.get("page_num", "0"))
        return parsed_bank_page, parsed_bank_id, parsed_time

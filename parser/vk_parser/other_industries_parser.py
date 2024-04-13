import os

import numpy as np

from utils import relative_path
from vk_parser.base_parser import VKBaseParser
from vk_parser.database import VKBaseDB, VkOtherIndustries
from vk_parser.queries import create_banks
from vk_parser.schemes import VKType


class VKOtherIndustriesParser(VKBaseParser):
    file = "vk_other_industries.npy"
    type = VKType.other

    def load_bank_list(self) -> None:
        path = relative_path(os.path.dirname(__file__), self.file)
        if not os.path.exists(path):
            raise FileNotFoundError(f"{self.file} not found")
        bank_arr = np.load(path, allow_pickle=True)
        group_ids = ",".join(bank_arr[:, 2])
        response = self.vk_api.groups_get_by_id(group_ids)
        if response is None:
            return None
        if bank_arr.shape[0] != len(response["response"]):
            self.logger.error("bank array and response have different length")
            raise Exception("bank array and response have different length")
        db_banks: list[VKBaseDB] = [
            VkOtherIndustries(id=bank[0], name=bank[1], vk_id=-vk_group["id"], domain=bank[2])
            for bank, vk_group in zip(bank_arr, response["response"])
        ]
        create_banks(db_banks)
        self.logger.info("bank list loaded")

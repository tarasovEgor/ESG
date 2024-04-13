from vk_parser.base_parser import VKBaseParser
from vk_parser.schemes import VKType


class VKBankParser(VKBaseParser):
    file = "vk_bank_list.npy"
    type = VKType.bank

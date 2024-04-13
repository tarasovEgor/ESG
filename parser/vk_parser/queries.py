from sqlalchemy import select

from common.database import get_sync
from vk_parser.database import VkBank, VKBaseDB, VkOtherIndustries
from vk_parser.schemes import VKType


def get_bank_list(bank_type: VKType) -> list[VKBaseDB]:
    with get_sync() as session:
        match bank_type:
            case VKType.bank:
                return session.scalars(select(VkBank).order_by(VkBank.id)).all()
            case VKType.other:
                return session.scalars(select(VkOtherIndustries).order_by(VkOtherIndustries.id)).all()
            case _:
                raise ValueError(f"Unknown bank type: {bank_type}")


def create_banks(bank_list: list[VKBaseDB]) -> None:
    with get_sync() as db:
        db.add_all(bank_list)
        db.commit()

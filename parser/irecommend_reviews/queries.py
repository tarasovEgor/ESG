from common.database import get_sync
from irecommend_reviews.database import IRecommend


def get_bank_list() -> list[IRecommend]:
    with get_sync() as db:
        bank_list = db.query(IRecommend).order_by(IRecommend.bank_id).all()
    return bank_list


def create_banks(bank_list: list[IRecommend]) -> None:
    with get_sync() as db:
        db.add_all(bank_list)
        db.commit()

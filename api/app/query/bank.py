from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import Bank
from app.database.models.bank import BankType
from app.schemes.bank_types import BankTypeVal


async def create_bank_element_type(db: AsyncSession, bank_type_name: BankTypeVal) -> BankType:
    bank_type: BankType | None = await db.scalar(select(BankType).filter(BankType.name == bank_type_name))
    if bank_type:
        return bank_type
    bank_type = BankType(name=bank_type_name)
    db.add(bank_type)
    await db.commit()
    return bank_type


async def get_bank_count(db: AsyncSession, bank_type_id: int) -> int:
    return await db.scalar(select(func.count(Bank.id)).filter(Bank.bank_type_id == bank_type_id))  # type: ignore


async def get_companies_list(db: AsyncSession, bank_type: BankTypeVal) -> list[Bank]:
    bank_type_id = select(BankType.id).filter(BankType.name == bank_type).limit(1).scalar_subquery()
    return await db.scalars(select(Bank).where(Bank.bank_type_id == bank_type_id))  # type: ignore


async def create_bank_type(db: AsyncSession) -> BankType:
    return await create_bank_element_type(db, BankTypeVal.bank)


async def create_broker_type(db: AsyncSession) -> BankType:
    return await create_bank_element_type(db, BankTypeVal.broker)


async def create_insurance_type(db: AsyncSession) -> BankType:
    return await create_bank_element_type(db, BankTypeVal.insurance)


async def create_mfo_type(db: AsyncSession) -> BankType:
    return await create_bank_element_type(db, BankTypeVal.mfo)


async def get_bank_list(db: AsyncSession) -> list[Bank]:
    return await get_companies_list(db, BankTypeVal.bank)


async def get_broker_list(db: AsyncSession) -> list[Bank]:
    return await get_companies_list(db, BankTypeVal.broker)


async def get_insurance_list(db: AsyncSession) -> list[Bank]:
    return await get_companies_list(db, BankTypeVal.insurance)


async def get_mfo_list(db: AsyncSession) -> list[Bank]:
    return await get_companies_list(db, BankTypeVal.mfo)


async def load_banks(db: AsyncSession, banks: list[Bank]) -> None:
    db.add_all(banks)
    await db.commit()

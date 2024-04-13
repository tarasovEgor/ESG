from app.database import SessionManager
from app.dataloader import BankParser, BrokerParser, InsuranceParser, MFOParser


async def load_data() -> None:
    # TODO change sessions for each class
    async with SessionManager().get_session_maker()() as db:
        bank = BankParser(db)
        broker = BrokerParser(db)
        insurance = InsuranceParser(db)
        mfo = MFOParser(db)
        await bank.load_banks()
        await broker.load_banks()
        await insurance.load_banks()
        await mfo.load_banks()
    # await asyncio.gather(bank.load_banks(), broker.load_banks(), insurance.load_banks(), mfo.load_banks())

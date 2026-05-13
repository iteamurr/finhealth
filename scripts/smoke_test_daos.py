import asyncio
import os
import sys
from datetime import date, timedelta

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from finhealth.infrastructure.database.dao import (
    SqlAlchemyCashFlowRepository,
    SqlAlchemyOrderRepository,
    SqlAlchemyReturnRepository,
    SqlAlchemySKURepository,
)


async def main() -> int:
    url = os.getenv("DATABASE_URL")
    if not url:
        print("ERROR: DATABASE_URL is not set", file=sys.stderr)
        return 1

    engine = create_async_engine(url, echo=False, pool_pre_ping=True)
    session_factory = async_sessionmaker(
        bind=engine, expire_on_commit=False
    )

    today = date.today()
    from_date = today - timedelta(days=30)

    try:
        async with session_factory() as session:
            sku_repo = SqlAlchemySKURepository(session)
            order_repo = SqlAlchemyOrderRepository(session)
            return_repo = SqlAlchemyReturnRepository(session)
            cashflow_repo = SqlAlchemyCashFlowRepository(session)

            skus = await sku_repo.find_all()
            orders = await order_repo.find_by_date_range(from_date, today)
            returns = await return_repo.find_by_date_range(from_date, today)
            cashflow = await cashflow_repo.find_by_date_range(
                from_date, today
            )

        print(f"Date range: {from_date} -> {today}")
        print(f"SKUs:           {len(skus)}")
        print(f"Orders:         {len(orders)}")
        print(f"Returns:        {len(returns)}")
        print(f"Cashflow rows:  {len(cashflow)}")

        counts = [len(skus), len(orders), len(returns), len(cashflow)]
        if any(c == 0 for c in counts):
            print("ERROR: at least one repository returned 0 rows")
            return 2
        print("OK: all repositories returned data")
        return 0
    finally:
        await engine.dispose()


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

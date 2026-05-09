from __future__ import annotations

import asyncio
import os
import random
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal

from dotenv import load_dotenv
from faker import Faker
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from finhealth.domain.entities.cashflow import CashFlowEntry
from finhealth.domain.entities.order import OrderEntity
from finhealth.domain.entities.return_ import ReturnEntity
from finhealth.domain.entities.sku import SKUEntity
from finhealth.infrastructure.database.models.cashflow import CashFlowEntryModel
from finhealth.infrastructure.database.models.order import OrderModel
from finhealth.infrastructure.database.models.return_ import ReturnModel
from finhealth.infrastructure.database.models.sku import SKUModel

SEED = 42
SKUS_PER_MARKETPLACE = 10
DAYS_BACK = 30
MARKETPLACES: tuple[str, ...] = ("WB", "OZON")
FASHION_CATEGORIES: tuple[str, ...] = (
    "Платье",
    "Футболка",
    "Джинсы",
    "Куртка",
    "Кроссовки",
    "Свитер",
    "Юбка",
    "Рубашка",
)
NON_FASHION_CATEGORIES: tuple[str, ...] = (
    "Чайник",
    "Наушники",
    "Лампа",
    "Кружка",
    "Книга",
    "Игрушка",
    "Рюкзак",
    "Пауэрбанк",
)
FASHION_RETURN_RATE = (0.25, 0.30)
NON_FASHION_RETURN_RATE = (0.05, 0.15)
ORDERS_PER_DAY_RANGE = (5, 50)
COMMISSION_RATE_RANGE = (0.15, 0.25)
LOGISTICS_RANGE = (50, 200)
AD_SPEND_RANGE = (0, 300)
LOSS_MAKING_SKU_COUNT = 3
TWOPLACES = Decimal("0.01")


@dataclass
class SeedPlan:
    skus: list[SKUEntity]
    orders: list[OrderEntity]
    returns: list[ReturnEntity]
    cashflow: list[CashFlowEntry]
    loss_making_sku_ids: list[str]


def _money(value: Decimal | float | int) -> Decimal:
    return Decimal(value).quantize(TWOPLACES, rounding=ROUND_HALF_UP)


def _pick_categories(fake: Faker) -> tuple[list[str], set[int]]:
    # 6 fashion SKUs out of 20 total, split across both marketplaces
    total = SKUS_PER_MARKETPLACE * len(MARKETPLACES)
    indices = list(range(total))
    random.shuffle(indices)
    fashion_indices = set(indices[:6])
    categories: list[str] = []
    for i in range(total):
        pool = FASHION_CATEGORIES if i in fashion_indices else NON_FASHION_CATEGORIES
        categories.append(random.choice(pool))
    return categories, fashion_indices


def _build_skus(fake: Faker) -> tuple[list[SKUEntity], set[str], list[str]]:
    categories, fashion_indices = _pick_categories(fake)
    skus: list[SKUEntity] = []
    fashion_sku_ids: set[str] = set()
    idx = 0
    for marketplace in MARKETPLACES:
        for n in range(SKUS_PER_MARKETPLACE):
            sku_id = f"{marketplace}-{n + 1:04d}"
            category = categories[idx]
            descriptor = fake.color_name()
            name = f"{category} {descriptor}"
            base_cost = Decimal(random.randint(200, 1200))
            skus.append(
                SKUEntity(
                    sku_id=sku_id,
                    name=name,
                    marketplace=marketplace,
                    cost_of_goods=_money(base_cost),
                )
            )
            if idx in fashion_indices:
                fashion_sku_ids.add(sku_id)
            idx += 1

    # Pick loss-making SKUs deterministically: take 3 random ones, raise their COGS
    all_ids = [s.sku_id for s in skus]
    random.shuffle(all_ids)
    loss_making_ids = all_ids[:LOSS_MAKING_SKU_COUNT]
    return skus, fashion_sku_ids, loss_making_ids


def _generate_orders(
    skus: list[SKUEntity],
    today: date,
) -> list[OrderEntity]:
    skus_by_market: dict[str, list[SKUEntity]] = {m: [] for m in MARKETPLACES}
    for sku in skus:
        skus_by_market[sku.marketplace].append(sku)

    orders: list[OrderEntity] = []
    counter = 0
    for delta in range(DAYS_BACK):
        sale_date = today - timedelta(days=DAYS_BACK - 1 - delta)
        for marketplace in MARKETPLACES:
            n_orders = random.randint(*ORDERS_PER_DAY_RANGE)
            for _ in range(n_orders):
                sku = random.choice(skus_by_market[marketplace])
                # Revenue centered around cost_of_goods * markup
                markup = Decimal(str(random.uniform(1.8, 3.2)))
                revenue = _money(sku.cost_of_goods * markup)
                commission_rate = Decimal(str(random.uniform(*COMMISSION_RATE_RANGE)))
                commission = _money(revenue * commission_rate)
                logistics = _money(random.randint(*LOGISTICS_RANGE))
                ad_spend = _money(random.randint(*AD_SPEND_RANGE))
                counter += 1
                order_id = f"ORD-{marketplace}-{counter:07d}"
                orders.append(
                    OrderEntity(
                        order_id=order_id,
                        sku_id=sku.sku_id,
                        marketplace=marketplace,
                        sale_date=sale_date,
                        revenue=revenue,
                        commission=commission,
                        logistics=logistics,
                        ad_spend=ad_spend,
                    )
                )
    return orders


def _generate_returns(
    orders: list[OrderEntity],
    fashion_sku_ids: set[str],
) -> list[ReturnEntity]:
    returns: list[ReturnEntity] = []
    counter = 0
    for order in orders:
        if order.sku_id in fashion_sku_ids:
            rate = random.uniform(*FASHION_RETURN_RATE)
        else:
            rate = random.uniform(*NON_FASHION_RETURN_RATE)
        if random.random() < rate:
            counter += 1
            # Return happens 1-7 days after sale
            return_date = order.sale_date + timedelta(days=random.randint(1, 7))
            returns.append(
                ReturnEntity(
                    return_id=f"RET-{order.marketplace}-{counter:07d}",
                    sku_id=order.sku_id,
                    marketplace=order.marketplace,
                    return_date=return_date,
                    amount=order.revenue,
                )
            )
    return returns


def _generate_cashflow(
    orders: list[OrderEntity],
    returns: list[ReturnEntity],
    today: date,
) -> list[CashFlowEntry]:
    # Index orders and returns by marketplace and week
    start_date = today - timedelta(days=DAYS_BACK - 1)
    entries: list[CashFlowEntry] = []

    def _week_index(d: date) -> int:
        return (d - start_date).days // 7

    weekly_net: dict[tuple[str, int], Decimal] = {}
    for order in orders:
        key = (order.marketplace, _week_index(order.sale_date))
        net = order.revenue - order.commission - order.logistics
        weekly_net[key] = weekly_net.get(key, Decimal("0")) + net
    for ret in returns:
        key = (ret.marketplace, _week_index(ret.return_date))
        weekly_net[key] = weekly_net.get(key, Decimal("0")) - ret.amount

    # Weekly payouts (positive) scheduled at end of each week
    sorted_keys = sorted(weekly_net.keys(), key=lambda k: (k[1], k[0]))
    for marketplace, week in sorted_keys:
        payout_date = start_date + timedelta(days=week * 7 + 6)
        if payout_date > today:
            payout_date = today
        amount = _money(weekly_net[(marketplace, week)])
        if amount > 0:
            entries.append(
                CashFlowEntry(
                    entry_date=payout_date,
                    marketplace=marketplace,
                    amount=amount,
                    entry_type="payout",
                )
            )
        elif amount < 0:
            entries.append(
                CashFlowEntry(
                    entry_date=payout_date,
                    marketplace=marketplace,
                    amount=amount,
                    entry_type="return_deduction",
                )
            )

    # Occasional fee charges (negative) sprinkled across the period
    for marketplace in MARKETPLACES:
        n_fees = random.randint(2, 4)
        for _ in range(n_fees):
            fee_date = start_date + timedelta(days=random.randint(0, DAYS_BACK - 1))
            fee_amount = _money(-Decimal(random.randint(500, 3500)))
            entries.append(
                CashFlowEntry(
                    entry_date=fee_date,
                    marketplace=marketplace,
                    amount=fee_amount,
                    entry_type="fee",
                )
            )

    entries.sort(key=lambda e: (e.entry_date, e.marketplace, e.entry_type))
    return entries


def _force_loss_making(
    skus: list[SKUEntity],
    orders: list[OrderEntity],
    returns: list[ReturnEntity],
    loss_making_sku_ids: list[str],
) -> None:
    # Compute per-SKU revenue/cost components and raise cost_of_goods until profit < 0
    by_sku: dict[str, dict[str, Decimal]] = {}
    for sku in skus:
        by_sku[sku.sku_id] = {
            "units_sold": Decimal("0"),
            "revenue": Decimal("0"),
            "commissions": Decimal("0"),
            "logistics": Decimal("0"),
            "ad_spend": Decimal("0"),
            "returns": Decimal("0"),
        }
    for order in orders:
        agg = by_sku[order.sku_id]
        agg["units_sold"] += Decimal("1")
        agg["revenue"] += order.revenue
        agg["commissions"] += order.commission
        agg["logistics"] += order.logistics
        agg["ad_spend"] += order.ad_spend
    for ret in returns:
        by_sku[ret.sku_id]["returns"] += ret.amount

    by_id = {sku.sku_id: sku for sku in skus}
    for sku_id in loss_making_sku_ids:
        sku = by_id[sku_id]
        agg = by_sku[sku_id]
        units = agg["units_sold"]
        if units == 0:
            sku.cost_of_goods = _money(Decimal("5000"))
            continue
        # profit_excl_cogs = revenue - commissions - logistics - returns - ad_spend
        profit_excl_cogs = (
            agg["revenue"]
            - agg["commissions"]
            - agg["logistics"]
            - agg["returns"]
            - agg["ad_spend"]
        )
        # We need cost_of_goods * units > profit_excl_cogs (cogs is per unit)
        min_cogs = profit_excl_cogs / units
        new_cogs = _money(min_cogs + Decimal(random.randint(80, 250)))
        if new_cogs <= 0:
            new_cogs = _money(Decimal("500"))
        sku.cost_of_goods = new_cogs


def build_plan(today: date | None = None) -> SeedPlan:
    fake = Faker("ru_RU")
    Faker.seed(SEED)
    random.seed(SEED)

    today = today or date.today()
    skus, fashion_sku_ids, loss_making_ids = _build_skus(fake)
    orders = _generate_orders(skus, today)
    returns = _generate_returns(orders, fashion_sku_ids)
    _force_loss_making(skus, orders, returns, loss_making_ids)
    cashflow = _generate_cashflow(orders, returns, today)
    return SeedPlan(
        skus=skus,
        orders=orders,
        returns=returns,
        cashflow=cashflow,
        loss_making_sku_ids=loss_making_ids,
    )


async def _truncate_all(session: AsyncSession) -> None:
    await session.execute(
        text(
            "TRUNCATE TABLE orders, returns, cashflow_entries, skus "
            "RESTART IDENTITY CASCADE"
        )
    )


async def _insert_plan(session: AsyncSession, plan: SeedPlan) -> None:
    session.add_all([SKUModel.from_entity(s) for s in plan.skus])
    session.add_all([OrderModel.from_entity(o) for o in plan.orders])
    session.add_all([ReturnModel.from_entity(r) for r in plan.returns])
    session.add_all([CashFlowEntryModel.from_entity(c) for c in plan.cashflow])


async def _print_counts(session: AsyncSession, plan: SeedPlan) -> None:
    sku_count = await session.scalar(select(func.count()).select_from(SKUModel))
    order_count = await session.scalar(select(func.count()).select_from(OrderModel))
    return_count = await session.scalar(select(func.count()).select_from(ReturnModel))
    cashflow_count = await session.scalar(
        select(func.count()).select_from(CashFlowEntryModel)
    )
    print("Seed complete.")
    print(f"  skus:             {sku_count}")
    print(f"  orders:           {order_count}")
    print(f"  returns:          {return_count}")
    print(f"  cashflow_entries: {cashflow_count}")
    print(f"  loss-making SKUs: {', '.join(plan.loss_making_sku_ids)}")


async def run_seed(database_url: str | None = None) -> None:
    load_dotenv()
    url = database_url or os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is not set")

    engine = create_async_engine(url, echo=False)
    session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    plan = build_plan()

    try:
        async with session_factory() as session:
            async with session.begin():
                await _truncate_all(session)
                await _insert_plan(session, plan)
            await _print_counts(session, plan)
    finally:
        await engine.dispose()


def main() -> None:
    asyncio.run(run_seed())


if __name__ == "__main__":
    main()

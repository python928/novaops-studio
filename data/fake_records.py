from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import date, timedelta


@dataclass(frozen=True, slots=True)
class DemoRecord:
    record_id: int
    title: str
    domain: str
    owner: str
    status: str
    score: int
    amount: float
    updated_on: str


def generate_demo_records(count: int = 30000, *, seed: int = 11) -> list[DemoRecord]:
    rng = random.Random(seed)
    today = date.today()

    products = (
        "Core Engine",
        "Auth Gateway",
        "Data Bridge",
        "Workflow Hub",
        "Client Portal",
        "Audit Stream",
        "Rule Studio",
        "Ops Toolkit",
    )
    domains = ("Operations", "Finance", "HR", "Sales", "Analytics", "Support")
    owners = (
        "Maya Ali",
        "Kareem N",
        "Noor M",
        "Adel H",
        "Rana S",
        "Lina T",
        "Yousef K",
        "Omar J",
    )
    statuses = ("Healthy", "At Risk", "Blocked", "Review")

    records: list[DemoRecord] = []
    for i in range(1, count + 1):
        title = f"{rng.choice(products)} v{rng.randint(1, 14)}"
        domain = rng.choice(domains)
        owner = rng.choice(owners)
        status = rng.choices(statuses, weights=(54, 23, 12, 11), k=1)[0]
        score = rng.randint(10, 99)
        amount = round(rng.uniform(1200.0, 95000.0), 2)
        updated_on = (today - timedelta(days=rng.randint(0, 150))).isoformat()

        records.append(
            DemoRecord(
                record_id=i,
                title=title,
                domain=domain,
                owner=owner,
                status=status,
                score=score,
                amount=amount,
                updated_on=updated_on,
            )
        )

    return records

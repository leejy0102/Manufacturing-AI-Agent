# incident_cases를 기반으로
# 과거 사건별 조치 이력을 가상으로 생성하고
# action_history 테이블에 저장하는 스크립트

import random
import pandas as pd

from app.database.connection import engine


# --------------------------------------------------
# 1. Incident Case 불러오기
# --------------------------------------------------

incident_cases = pd.read_sql(
    """
    SELECT
        case_id,
        downtime_reason,
        downtime_minutes
    FROM incident_cases
    ORDER BY case_id;
    """,
    engine
)


# --------------------------------------------------
# 2. Downtime 원인별 가능한 조치 정의
# 실제 회사 데이터가 아닌 포트폴리오용 Synthetic Action
# --------------------------------------------------

ACTION_MAP = {

    "Filler Jam": [
        "Clear Jammed Containers",
        "Adjust Filler Guide",
        "Check Filler Sensor",
    ],

    "Sensor Error": [
        "Clean Sensor",
        "Realign Sensor",
        "Check Sensor Connection",
    ],

    "Conveyor Stop": [
        "Clear Conveyor Blockage",
        "Inspect Conveyor Drive",
        "Reset Conveyor Interlock",
    ],

    "Packer Fault": [
        "Reset Packer",
        "Inspect Packer Mechanism",
        "Adjust Packer Setting",
    ],

    "Washer Fault": [
        "Inspect Washer",
        "Reset Washer",
        "Adjust Washer Setting",
    ],

    "Operator Adjustment": [
        "Adjust Operating Setting",
        "Standardize Operating Condition",
    ],

    "Upstream/Downstream Delay": [
        "Adjust Line Balance",
        "Coordinate Upstream Downstream Flow",
    ],

    "Utility Issue": [
        "Check Utility Supply",
        "Restore Utility Condition",
    ],

    "Container Damage": [
        "Remove Damaged Containers",
        "Inspect Container Flow",
    ],
}


# --------------------------------------------------
# 3. Action History 생성
# --------------------------------------------------

random.seed(42)

records = []


for _, case in incident_cases.iterrows():

    reason = case["downtime_reason"]

    # 정의되지 않은 원인은 일반 점검 조치 사용
    possible_actions = ACTION_MAP.get(
        reason,
        [
            "Inspect Process Condition",
            "Check Equipment Condition",
        ]
    )

    action_type = random.choice(possible_actions)

    # 기본 성공 확률
    success_probability = 0.75

    success = random.random() < success_probability

    # 성공했으면 기존 downtime보다 빠르게 복구되는 것으로 가정
    if success:

        recovery_minutes = max(
            1,
            case["downtime_minutes"]
            * random.uniform(0.3, 0.8)
        )

        effectiveness_score = random.uniform(
            0.65,
            0.95
        )

    else:

        recovery_minutes = (
            case["downtime_minutes"]
            * random.uniform(0.9, 1.3)
        )

        effectiveness_score = random.uniform(
            0.10,
            0.50
        )


    records.append(
        {
            "case_id": case["case_id"],
            "action_type": action_type,
            "success": success,
            "recovery_minutes": round(
                recovery_minutes,
                1
            ),
            "effectiveness_score": round(
                effectiveness_score,
                3
            ),
        }
    )


# --------------------------------------------------
# 4. DataFrame 생성
# --------------------------------------------------

action_history = pd.DataFrame(records)

action_history.insert(
    0,
    "action_id",
    range(1, len(action_history) + 1)
)


# --------------------------------------------------
# 5. PostgreSQL 저장
# --------------------------------------------------

action_history.to_sql(
    "action_history",
    engine,
    if_exists="replace",
    index=False
)


print("action_history 테이블 생성 완료")
print(f"총 Action 수: {len(action_history)}")

print("\nSample:")
print(action_history.head())
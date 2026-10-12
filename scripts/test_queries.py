# get_production_data 함수 테스트
from app.database.queries import get_production_data

result = get_production_data(
    line_name="CAN1",
    start_date="2026-01-01",
    end_date="2026-01-31"
)

# print(result.head())
# print("조회 행 수:", len(result))


# get_kpi_summary 함수 테스트
from app.database.queries import get_kpi_summary

kpi_result = get_kpi_summary(
    line_name="CAN1",
    start_date="2026-01-01",
    end_date="2026-01-31"
)

# print(kpi_result)


# get_downtime_summary 함수 테스트
from app.database.queries import get_downtime_summary

downtime_result = get_downtime_summary(
    line_id=3,
    start_date="2026-01-01",
    end_date="2026-01-31"
)

# print(downtime_result.head(10))


# get_performance_loss_summary 함수 테스트
from app.database.queries import get_performance_loss_summary

performance_loss_result = get_performance_loss_summary(
    line_id=3,
    start_date="2026-01-01",
    end_date="2026-01-31"
)

# print(performance_loss_result)


# get_quality_summary 함수 테스트
from app.database.queries import get_quality_summary

quality_result = get_quality_summary(
    line_name="CAN1",
    start_date="2026-01-01",
    end_date="2026-01-31"
)

# print(quality_result)


# get_planned_downtime_summary 함수 테스트
from app.database.queries import get_planned_downtime_summary

planned_downtime_result = get_planned_downtime_summary(
    line_id=3,
    start_date="2026-01-01",
    end_date="2026-01-31"
)

print(planned_downtime_result)
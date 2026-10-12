# production_data_tool 동작 테스트
from app.tools.manufacturing_tools import production_data_tool

result = production_data_tool.invoke({
    "line_name": "CAN1",
    "start_date": "2026-01-01",
    "end_date": "2026-01-05"
})

# print(result)


# kpi_summary_tool 동작 테스트
from app.tools.manufacturing_tools import kpi_summary_tool

kpi_result = kpi_summary_tool.invoke({
    "line_name": "CAN1",
    "start_date": "2026-01-01",
    "end_date": "2026-01-31"
})

# print(kpi_result)


# downtime_summary_tool 동작 테스트
from app.tools.manufacturing_tools import downtime_summary_tool

downtime_result = downtime_summary_tool.invoke({
    "line_id": 3,
    "start_date": "2026-01-01",
    "end_date": "2026-01-31"
})

# print(downtime_result)


# performance_loss_summary_tool 동작 테스트
from app.tools.manufacturing_tools import performance_loss_summary_tool

performance_loss_result = performance_loss_summary_tool.invoke({
    "line_id": 3,
    "start_date": "2026-01-01",
    "end_date": "2026-01-31"
})

# print(performance_loss_result)


# quality_summary_tool 동작 테스트
from app.tools.manufacturing_tools import quality_summary_tool

quality_result = quality_summary_tool.invoke({
    "line_name": "CAN1",
    "start_date": "2026-01-01",
    "end_date": "2026-01-31"
})

print(quality_result)


# planned_downtime_summary_tool 동작 테스트
from app.tools.manufacturing_tools import planned_downtime_summary_tool

planned_downtime_result = planned_downtime_summary_tool.invoke({
    "line_id": 3,
    "start_date": "2026-01-01",
    "end_date": "2026-01-31"
})

print(planned_downtime_result)
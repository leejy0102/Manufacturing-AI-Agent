# # LangGraph Manufacturing Agent 전체 동작 테스트 #첫번째 질문
# from app.agent.graph import manufacturing_agent

# result = manufacturing_agent.invoke(
#     {
#         "messages": [
#             {
#                 "role": "user",
#                 "content": "CAN1 라인의 2026년 1월 평균 OEE를 알려줘."
#             }
#         ]
#     }
# )

# print("최종 응답:")
# print(result["messages"][-1].content)


# LangGraph Manufacturing Agent 복합 분석 테스트 # 두번째 질문

# from app.agent.graph import manufacturing_agent

# result = manufacturing_agent.invoke(
#     {
#         "messages": [
#             {
#                 "role": "user",
#                 "content": (
#                     "CAN1 라인의 2026년 1월 OEE가 왜 낮았는지 분석해줘. "
#                     "KPI, 비계획정지, Performance Loss를 함께 보고 "
#                     "주요 원인을 설명해줘."
#                 )
#             }
#         ]
#     }
# )

# print("최종 응답:")
# print(result["messages"][-1].content)


# LangGraph Manufacturing Agent
# DB 분석 Tool과 SOP RAG Tool을 함께 사용하는지 테스트 #세번째 질문

from app.agent.graph import manufacturing_agent

result = manufacturing_agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": (
                    "CAN1의 2026년 1월 평균 OEE 알려줘."
                )
            },
            {
                "role": "assistant",
                "content": (
                    "CAN1의 2026년 1월 평균 OEE는 83.8%입니다."
                )
            },
            {
                "role": "user",
                "content": (
                    "그럼 2월은?"
                )
            }
        ]
    }
)

print("최종 응답:")
print(result["messages"][-1].content)
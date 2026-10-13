# SOP Vector Search 테스트
# 자연어 질문과 의미적으로 가까운 SOP Chunk가 검색되는지 확인
from app.database.queries import search_sop_documents


query = "Filler에서 병이 자꾸 막힐 때 어떻게 대응해야 해?"

results = search_sop_documents(
    query=query,
    top_k=3
)

print(f"질문: {query}\n")

for index, result in enumerate(results, start=1):

    print(f"[검색 결과 {index}]")
    print("파일:", result["source_file"])
    print("거리:", round(result["distance"], 4))
    print("내용:")
    print(result["content"])
    print("-" * 60)
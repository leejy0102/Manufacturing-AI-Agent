import pandas as pd

lines = [
    [1, "BTL2", "BOTTLE", 500],
    [2, "BTL5", "BOTTLE", 500],
    [3, "CAN1", "CAN", 1000],
    [4, "CAN2", "CAN", 1000],
    [5, "PET1", "PET", 200],
    [6, "PET2", "PET", 200],
]

df_lines = pd.DataFrame(
    lines,
    columns=["line_id", "line_name", "line_type", "ideal_speed_per_min"]
)

print(df_lines)

equipment = [
    # BTL2
    [1, 1, "BTL2_Unpacker", "Unpacker"],
    [2, 1, "BTL2_Washer", "Washer"],
    [3, 1, "BTL2_Filler", "Filler"],
    [4, 1, "BTL2_Pasteurizer", "Pasteurizer"],
    [5, 1, "BTL2_Labeler", "Labeler"],
    [6, 1, "BTL2_Packer", "Packer"],

    # BTL5
    [7, 2, "BTL5_Unpacker", "Unpacker"],
    [8, 2, "BTL5_Washer", "Washer"],
    [9, 2, "BTL5_Filler", "Filler"],
    [10, 2, "BTL5_Pasteurizer", "Pasteurizer"],
    [11, 2, "BTL5_Labeler", "Labeler"],
    [12, 2, "BTL5_Packer", "Packer"],

    # CAN1
    [13, 3, "CAN1_Depalletizer", "Depalletizer"],
    [14, 3, "CAN1_Filler", "Filler"],
    [15, 3, "CAN1_Pasteurizer", "Pasteurizer"],
    [16, 3, "CAN1_Packer", "Packer"],

    # CAN2
    [17, 4, "CAN2_Depalletizer", "Depalletizer"],
    [18, 4, "CAN2_Filler", "Filler"],
    [19, 4, "CAN2_Pasteurizer", "Pasteurizer"],
    [20, 4, "CAN2_Packer", "Packer"],

    # PET1
    [21, 5, "PET1_Blower", "Blower"],
    [22, 5, "PET1_Filler", "Filler"],
    [23, 5, "PET1_Labeler", "Labeler"],
    [24, 5, "PET1_Packer", "Packer"],

    # PET2
    [25, 6, "PET2_Blower", "Blower"],
    [26, 6, "PET2_Filler", "Filler"],
    [27, 6, "PET2_Labeler", "Labeler"],
    [28, 6, "PET2_Packer", "Packer"],
]

df_equipment = pd.DataFrame(
    equipment,
    columns=["equipment_id", "line_id", "equipment_name", "equipment_type"]
)

print(df_equipment)

products = [
    [1, "Cass Fresh", "BOTTLE", 500],
    [2, "Cafri", "BOTTLE", 330],

    [3, "Cass Fresh", "CAN", 355],
    [4, "Cass Fresh", "CAN", 500],
    [5, "Cass Light", "CAN", 500],
    [6, "Hanmac", "CAN", 500],
    [7, "OB", "CAN", 500],
    [8, "Fillgood", "CAN", 500],
    [9, "Budweiser", "CAN", 500],

    [10, "Cass Fresh", "PET", 2000],
    [11, "Cass Light", "PET", 2000],
    [12, "Fillgood", "PET", 2000],
]

df_products = pd.DataFrame(
    products,
    columns=["product_id", "brand_name", "package_type", "volume_ml"]
)

print(df_products)

df_lines.to_csv("data/lines.csv", index=False)
df_equipment.to_csv("data/equipment.csv", index=False)
df_products.to_csv("data/products.csv", index=False)

print("마스터 데이터 저장 완료")
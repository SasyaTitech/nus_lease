from __future__ import annotations

DISTRICT_TO_SECTORS = {
    "01": {"01", "02", "03", "04", "05", "06"},
    "02": {"07", "08"},
    "03": {"14", "15", "16"},
    "04": {"09", "10"},
    "05": {"11", "12", "13"},
    "06": {"17"},
    "07": {"18", "19"},
    "08": {"20", "21"},
    "09": {"22", "23"},
    "10": {"24", "25", "26", "27"},
    "11": {"28", "29", "30"},
    "12": {"31", "32", "33"},
    "13": {"34", "35", "36", "37"},
    "14": {"38", "39", "40", "41"},
    "15": {"42", "43", "44", "45"},
    "16": {"46", "47", "48"},
    "17": {"49", "50", "81"},
    "18": {"51", "52"},
    "19": {"53", "54", "55", "82"},
    "20": {"56", "57"},
    "21": {"58", "59"},
    "22": {"60", "61", "62", "63", "64"},
    "23": {"65", "66", "67", "68"},
    "24": {"69", "70", "71"},
    "25": {"72", "73"},
    "26": {"77", "78"},
    "27": {"75", "76"},
    "28": {"79", "80"},
}

SECTOR_TO_DISTRICT = {
    sector: district
    for district, sectors in DISTRICT_TO_SECTORS.items()
    for sector in sectors
}


def postal_sector(postal_code: str | int | None) -> str | None:
    if postal_code is None:
        return None
    digits = "".join(char for char in str(postal_code) if char.isdigit())
    if len(digits) < 2:
        return None
    return digits[:2]


def district_from_postal_code(postal_code: str | int | None) -> str | None:
    sector = postal_sector(postal_code)
    if sector is None:
        return None
    return SECTOR_TO_DISTRICT.get(sector)

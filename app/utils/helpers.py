def format_address(addr: dict) -> str:
    attrs = addr.get("@attributes", {})

    parts = []

    # Сначала индекс
    index = attrs.get("Индекс")
    if index:
        parts.append(index)

    # Регион
    region = addr.get("Регион", {}).get("@attributes", {}).get("НаимРегион")
    if region:
        parts.append(region.upper())

    # Город
    city_type = addr.get("Город", {}).get("@attributes", {}).get("ТипГород", "")
    city_name = addr.get("Город", {}).get("@attributes", {}).get("НаимГород")
    if city_name:
        parts.append(f"{city_type} {city_name}".strip().upper())

    # Улица
    street_type = addr.get("Улица", {}).get("@attributes", {}).get("ТипУлица", "")
    street_name = addr.get("Улица", {}).get("@attributes", {}).get("НаимУлица")
    if street_name:
        parts.append(f"{street_type} {street_name}".strip().upper())

    # Дом
    if "Дом" in attrs:
        parts.append(attrs["Дом"].strip())

    # Корпус / Строение / Помещение и т.п.
    for key in ["Корпус", "Строение", "Литера", "Помещ", "Офис", "Кварт"]:
        if key in attrs:
            parts.append(f"{key}. {attrs[key]}")

    return ", ".join(parts)


def extract_main_ogrn(data: dict) -> str:
    """Возвращает ОГРН головной организации"""
    return data.get("СвЮЛ", {}).get("@attributes", {}).get("ОГРН", "")


def extract_branch_kpps(data: dict) -> list[str]:
    """Извлекает список всех КПП филиалов"""
    филиалы = data.get("СвЮЛ", {}).get("СвПодразд", {}).get("СвФилиал", [])
    return [
        филиал.get("СвУчетНОФилиал", {}).get("@attributes", {}).get("КПП")
        for филиал in филиалы
        if филиал.get("СвУчетНОФилиал", {}).get("@attributes", {}).get("КПП")
    ]


def is_branch_kpp_exist(data: dict, kpp_to_check: str) -> bool:
    """Проверяет, есть ли такой КПП среди филиалов"""
    return kpp_to_check in extract_branch_kpps(data)

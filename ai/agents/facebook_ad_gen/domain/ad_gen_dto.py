from typing import TypedDict


class AdGenDto(TypedDict):
    objective: str
    details: str
    brand_persona: dict


def convert_to_dict(ad_dto: AdGenDto) -> dict:
    return {
        "objective": ad_dto['objective'],
        "details": ad_dto['details'],  # Fixed value as specified
        "brand_persona": ad_dto['brand_persona'],
    }
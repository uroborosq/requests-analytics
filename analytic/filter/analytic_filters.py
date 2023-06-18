import datetime
from copy import copy


def manager_time_filter(manager: str, date_begin: datetime.date, date_end: datetime.date, requests):
    result = {}

    if manager != 'Все':
        for i in requests:
            if requests[i].manager == manager:
                result[i] = requests[i]
    else:
        result = copy(requests)

    for i in result:
        if not date_end >= result[i] >= date_begin:
            result.pop(i)

    return result


def manager_filter(requests: dict, manager: str) -> dict:
    if manager == 'Все сотрудники':
        return requests
    filtered = {}
    for i in requests:
        if requests[i].manager == manager:
            filtered[i] = requests[i]
    return filtered


def warranty_type_filter(requests: dict, request_type: list[str]) -> dict:
    filtered = {}
    for i in requests:
        if requests[i].warranty in request_type:
            filtered[i] = requests[i]

    return filtered

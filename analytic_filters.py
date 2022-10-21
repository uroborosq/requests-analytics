import datetime
from copy import copy


def filter(self, manager: str, date_begin: datetime.date, date_end: datetime.date, requests):
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


import requests
from get_data import get_event_data


def getReqest(destID):
    return get_event_data({
        'destID': destID,
    })


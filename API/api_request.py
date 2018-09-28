import requests


def public_request(url, request, params=None):
    r = requests.get(url+request, params=params)
    if not r.status_code == requests.codes.ok:
        r.raise_for_status()
        return
    return r.json()
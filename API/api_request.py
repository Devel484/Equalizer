"""
author: Devel484
"""
import requests
import API.log


def public_request(url, request, params=None):
    """
    Makes a public http request
    :param url: basic URL
    :param request: request URL
    :param params: parameters
    :return: JSON result
    """
    r = requests.get(url+request, params=params)
    if not r.status_code == requests.codes.ok:
        API.log.log_and_print("API_response.txt", "[%s]%s\nReason:%s" % (r.status_code, r.url, r.reason))
        r.raise_for_status()
        return
    return r.json()

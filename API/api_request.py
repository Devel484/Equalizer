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
    try:
        r = requests.get(url+request, params=params, timeout=2)
    except Exception as e:
        API.log.log("request.txt", e)
        return None
    if not r.status_code == requests.codes.ok:
        API.log.log_and_print("API_response.txt", "[%s]%s\nReason:%s" % (r.status_code, r.url, r.reason))
        return None
    return r.json()

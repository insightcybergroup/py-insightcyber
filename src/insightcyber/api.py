# src/insightcyber/api.py


import requests
import hashlib
import configparser
import os
import atexit


ICG_URL_STEM="https://platform.insightcyber.com"

_session=None

def cleanup():
    if _session["sess"]:
        response = requests.post(
            f"{ICG_URL_STEM}/r/signout",
            cookies=_session,
            timeout=10,
        )
        response.raise_for_status()
        #print ("SIGNED OUT")
atexit.register(cleanup)



def hello():
    """
    Say hello, so the caller knows the library is installed.
    """
    print ("Hello from InsightCyber")


class SessionException(Exception):
    pass

def _get_session():
    global _session
    if _session is not None:
        return

    try:
        cp = configparser.ConfigParser()
        cp.read(["./.insightcyberrc",os.path.expanduser("~/.insightcyberrc")])
        user = cp["insightcyber"]["user"]
        token = cp["insightcyber"]["token"]

        payload = {
                "email": user,
                "tag": token[0:16],
        }
    except:
        raise SessionException("no config or invalid username/token")

    response = requests.put(
            f"{ICG_URL_STEM}/api/session",
            json=payload,
            headers=None,
            timeout=10,
    )
    response.raise_for_status()
    nonce = response.json()["nonce"]
    nonce_secret = nonce + token
    cookie = hashlib.sha256(nonce_secret.encode()).hexdigest()

    _session = {"email":user, "sess":cookie}

def get_sensors():
    """
    Returns an array of sensor objects.
    """
    _get_session()
    response = requests.get(
            f"{ICG_URL_STEM}/r/networks",
            cookies = _session,
            timeout = 10,
    )
    response.raise_for_status()
    return response.json()

"""
Discord OAuth2 Redirect
"""


import json
from datetime import datetime


def middleware(event, context):
    pass


def lambda_handler(event, context):
    res = middleware(event, context)

    print("res", json.dumps(res))

    return res

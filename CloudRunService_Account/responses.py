import json

def error(message):
    return json.dumps({
        "current_balance": 
        {
            "cash":None,
            "issuers":[]
        },
        "business_errors": ["{}".format(message)]
    })


def sucess(message):
    return json.dumps(message)
import os
import sys
from flask import Flask, request
from flask import jsonify
import requests
import json
from datetime import datetime, timedelta
from google.cloud import firestore
import google.cloud.exceptions
import constants



app = Flask(__name__)

def getErrorResponse(error):
    jsonRaw = {
        'business_errors': ['{}'.format(error)]
    }
    jsonResponse = app.response_class(
        response=json.dumps(jsonRaw),
        status=400,
        mimetype='application/json'
    )
    return jsonResponse

def getSucesfullResponse(account):
    jsonRaw = account
    jsonResponse = app.response_class(
        response=json.dumps(jsonRaw),
        status=200,
        mimetype='application/json'
    )
    return jsonResponse


def getLastid():
    id=0
    try: 
        db = firestore.Client()
        accounts_ref = db.collection("accounts")
        query = accounts_ref.order_by("id", direction=firestore.Query.DESCENDING).limit(1)
        try:
            account_result = query.get()
            if len(account_result)>0:
                account = account_result[0].to_dict()
                account_id =account["id"]
                id = account_id+1
            return id
        except google.cloud.exceptions.NotFound as error:
            return getErrorResponse(constants.ERROR_ID)
    except BaseException as error:
        return getErrorResponse(constants.ERROR_DB)
    

def createAccount(cash):
    try: 
        db = firestore.Client()
        account ={
            "id": getLastid(),
            "cash": cash
        }
        db.collection(u'accounts').add(account)
        account["issuers"]=[]
        return getSucesfullResponse(account)
    except BaseException as error:
        return getErrorResponse(constants.ERROR_DB)


@app.route('/accounts', methods=['POST'])
def consultaSaldo():
    try:             
        if(request.headers['Content-Type'] == 'application/json'):
            content = json.loads(request.get_data())
            if content != None:
                if "cash" in content:
                    if content["cash"]>0:
                        return createAccount(content["cash"])
                    return getErrorResponse(constants.ERROR_CASH)
                return getErrorResponse(constants.ERROR_REQUEST)
            return getErrorResponse(constants.ERROR_REQUEST)
        return getErrorResponse(constants.ERROR_REQUEST)
    except BaseException as error:
        return getErrorResponse(error)

        
if __name__ == '__main__':
     app.run(host='0.0.0.0', port=8080)


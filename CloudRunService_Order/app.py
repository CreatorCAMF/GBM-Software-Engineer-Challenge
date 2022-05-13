from ast import Return
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
        "current_balance": 
        {
            "cash":None,
            "issuers":[]
        },
        "business_errors": ["{}".format(error)]
    }
    jsonResponse = app.response_class(
        response=json.dumps(jsonRaw),
        status=400,
        mimetype="application/json"
    )
    return jsonResponse

def getSucesfullResponse(account):
    jsonRaw = account
    jsonResponse = app.response_class(
        response=json.dumps(jsonRaw),
        status=200,
        mimetype="application/json"
    )
    return jsonResponse


def getAccount(id):
    id=0
    try: 
        db = firestore.Client()
        accounts_ref = db.collection("accounts")
        query = accounts_ref.where(u"id", u"==", id)
        try:
            account_result = query.get()
            if len(account_result)>0:
                account = account_result[0]
                account_id =account.id
                account = account_result[0].to_dict()
                account["id"] = account_id
                return account
            else: 
                return None
        except google.cloud.exceptions.NotFound as error:
            return getErrorResponse(constants.ERROR_ID)
    except BaseException as error:
        return getErrorResponse(constants.ERROR_DB)


def verifyNotDuplicateOrder(account_id, order):
    try: 
        db = firestore.Client()
        orders_ref = db.collection("orders")
        query = orders_ref.where(u"account_id", u"==", account_id).where(u"operation", u"==", order["operation"]).where(u"issuer_name", u"==", order["issuer_name"]).where(u"total_shares", u"==",  order["total_shares"]).where(u"timestamp", u">=", order["timestamp"]-(60*5))
        try:
            orders_result = query.get()
            print(orders_result)
            if len(orders_result)>0:
                return False
            else:
                order["account_id"]=account_id
                orders_ref.add(order)
                return True
        except google.cloud.exceptions.NotFound as error:
            print(error)
            return True
    except BaseException as error:
        print(error)
        return getErrorResponse(constants.ERROR_DB)


def createIssuer(account_id,order):
    try: 
        db = firestore.Client()
        issuer ={
            "account_id": account_id,
            "issuer_name": order["issuer_name"],
            "total_shares": order["total_shares"],
            "share_price": order["share_price"]
        }
        db.collection(u"issuers").add(issuer)
    except BaseException as error:
        return getErrorResponse(constants.ERROR_DB)


def updateIssuer(issuer,order):
    try: 
        db = firestore.Client()
        print(issuer["id"])
        issuers_ref = db.collection("issuers").document(issuer["id"])
        account= issuers_ref.get()
        account= account.to_dict()
        print(account)
        issuers_ref.update({u"total_shares": (issuer["total_shares"]+order["total_shares"])})
        issuers_ref.update({u"share_price": order["share_price"]})
    except BaseException as error:
        return getErrorResponse(constants.ERROR_DB)


def deleteIssuer(issuer):
    try: 
        db = firestore.Client()
        db.collection("issuers").document(issuer["id"]).delete()
    except BaseException as error:
        return getErrorResponse(constants.ERROR_DB)


def updateAccount(account,order):
    operation=1 if order["operation"]=="BUY" else-1
    print(operation)
    try: 
        db = firestore.Client()
        account_ref = db.collection("accounts").document(account["id"])
        account_ref.update({u"cash": account["cash"]+((order["total_shares"]*order["share_price"])*operation)})
    except BaseException as error:
        return getErrorResponse(constants.ERROR_DB)


def buySellIssuer(account_id, order):
    try: 
        db = firestore.Client()
        issuers_ref = db.collection("issuers")
        query = issuers_ref.where(u"account_id", u"==", account_id).where(u"issuer_name", u"==", order["issuer_name"])
        try:
            issuers_result = query.get()
            print(issuers_result)
            if len(issuers_result)>0:
                issuer = issuers_result[0]
                issuer_id =issuer.id
                issuer = issuers_result[0].to_dict()
                issuer["id"]=issuer_id
                operation=1 if order["operation"]=="BUY" else-1
                order["total_shares"]=order["total_shares"]*operation
                if (issuer["total_shares"]+order["total_shares"])>0:
                    print("Update Issuer")
                    print(issuer)
                    print(order)
                    updateIssuer(issuer,order)
                    return True
                elif (issuer["total_shares"]+order["total_shares"])==0:
                    print("delete Issuer")
                    deleteIssuer(issuer)
                    return True
                else:
                    print("menor a 0")
                    print(order["operation"])
                    return False
            else:
                if order["operation"]=="BUY":
                    createIssuer(account_id, order)
                    return True
                else:
                    return False
        except google.cloud.exceptions.NotFound as error:
            createIssuer(account_id, order)
            return True
    except BaseException as error:
        print(error)
        return getErrorResponse(constants.ERROR_DB)


def getAccountIssuers(account_id):
    cash=None
    issuers=[]
    try: 
        db = firestore.Client()
        account_ref = db.collection("accounts").document(account_id)
        try:
            account= account_ref.get()
            account= account.to_dict()
            cash = account["cash"]
            issuers_ref = db.collection("issuers")
            query = issuers_ref.where(u"account_id", u"==", account_id)
            issuers_result = query.get()
            for issuer in issuers_result:
                issuer=issuer.to_dict()
                del issuer["account_id"]
                issuers.append(issuer)
            response ={
                "current_balance": 
                {
                    "cash":cash,
                    "issuers":issuers
                },
                "business_errors":[]
            }
            return getSucesfullResponse(response)
        except google.cloud.exceptions.NotFound as error:
            return getErrorResponse(constants.ERROR_ID)
    except BaseException as error:
        print(error)
        return getErrorResponse(constants.ERROR_DB)
    

def buysellShare(id, order):
    account = getAccount(id)
    if account is not None:
        operation=1 if order["operation"]=="BUY" else-1
        if account["cash"]-((order["total_shares"]*order["share_price"])*operation)>=0:
            print("Antes de validar orden duplicada")
            print(account)
            if verifyNotDuplicateOrder(account["id"],order):
                if buySellIssuer(account["id"],order):
                    print("Entro")
                    updateAccount(account,order)
                else:
                    return getErrorResponse(constants.ERROR_STOCKS)
                return getAccountIssuers(account["id"])
            else:
                print("orden duplicada")
                return getErrorResponse(constants.ERROR_DUPLICATE_ORDER)
        else:
            return getErrorResponse(constants.ERROR_CASH)
    else:
        return getErrorResponse(constants.ERROR_ID)


    


@app.route("/accounts/<id>/orders", methods=["POST"])
def postOrders(id):
    try:             
        print(id)
        if(request.headers["Content-Type"] == "application/json"):
            content = request.json
            print(content)
            if content != None:
                if "timestamp" in content and "operation" in content and "issuer_name" in content and "total_shares" in content and "share_price" in content:
                    if content["operation"] in constants.OPERATION_TYPE and content["total_shares"]>0 and content["share_price"]>0:
                        hour=datetime.datetime.fromtimestamp(content["timestamp"]).hour
                        print(hour)
                        if hour > 6 and hour<15:
                            print("Empezamos")
                            return buysellShare(id,content)
                        return getErrorResponse(constants.ERROR_HOURS)  
                    return getErrorResponse(constants.ERROR_CASH)
                return getErrorResponse(constants.ERROR_REQUEST)
            return getErrorResponse(constants.ERROR_REQUEST)
        return getErrorResponse(constants.ERROR_REQUEST)
    except BaseException as error:
        return getErrorResponse(error)

        
if __name__ == "__main__":
     app.run(host="0.0.0.0", port=8080)


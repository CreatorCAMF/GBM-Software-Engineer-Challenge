from google.cloud import firestore
import google.cloud.exceptions
from exceptions import GBMException
import constants

def createIssuer(account_id,order):
    try: 
        db = firestore.Client()
        issuer ={
            "account_id": account_id,
            "issuer_name": order["issuer_name"],
            "total_shares": order["total_shares"],
            "share_price": abs(order["share_price"])
        }
        db.collection(u"issuers").add(issuer)
    except BaseException as error:
        raise GBMException(constants.ERROR_DB)


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
        raise GBMException(constants.ERROR_DB)


def deleteIssuer(issuer):
    try: 
        db = firestore.Client()
        db.collection("issuers").document(issuer["id"]).delete()
    except BaseException as error:
        raise GBMException(constants.ERROR_DB)


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
            return response
        except google.cloud.exceptions.NotFound as error:
            raise GBMException(constants.ERROR_ID)
    except BaseException as error:
        print(error)
        raise GBMException(constants.ERROR_DB)


def buySellIssuer(account_id, order):
    try: 
        db = firestore.Client()
        issuers_ref = db.collection("issuers")
        query = issuers_ref.where(u"account_id", u"==", account_id).where(u"issuer_name", u"==", order["issuer_name"])
        try:
            issuers_result = query.get()
            if len(issuers_result)>0:
                issuer = issuers_result[0]
                issuer_id =issuer.id
                issuer = issuers_result[0].to_dict()
                issuer["id"]=issuer_id
                if (issuer["total_shares"]+order["total_shares"])>0:
                    updateIssuer(issuer,order)
                    return True
                elif (issuer["total_shares"]+order["total_shares"])==0:
                    deleteIssuer(issuer)
                    return True
                else:
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
        raise GBMException(constants.ERROR_DB)
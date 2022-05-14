from google.cloud import firestore
import google.cloud.exceptions
from exceptions import GBMException
import constants


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
        except google.cloud.exceptions.NotFound:
            raise GBMException(constants.ERROR_ID)
    except BaseException:
        raise GBMException(constants.ERROR_REQUEST)


def createAccount(cash):
    try: 
        db = firestore.Client()
        account ={
            "id": getLastid(),
            "cash": cash
        }
        db.collection(u'accounts').add(account)
        account["issuers"]=[]
        return account
    except BaseException:
        raise GBMException(constants.ERROR_REQUEST)


def getAccount(id):
    try: 
        db = firestore.Client()
        accounts_ref = db.collection("accounts")
        query = accounts_ref.where(u"id", u"==", int(id))
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
        except google.cloud.exceptions.NotFound:
            raise GBMException(constants.ERROR_ID)
    except BaseException:
        raise GBMException(constants.ERROR_DB)


def updateAccount(account,order):
    try: 
        db = firestore.Client()
        account_ref = db.collection("accounts").document(account["id"])
        account_ref.update({u"cash": account["cash"]+(order["total_shares"]*order["share_price"])})
    except BaseException:
        raise GBMException(constants.ERROR_DB)



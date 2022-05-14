from google.cloud import firestore
import google.cloud.exceptions
from exceptions import GBMException
import constants

def verifyNotDuplicateOrder(account_id, order):
    print(account_id)
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
        raise GBMException(constants.ERROR_DB)
import pytz
import constants
from datetime import datetime
from flask import Flask, request
from exceptions import GBMException
from accounts import getAccount, updateAccount
from issuers import getAccountIssuers, buySellIssuer
from orders import verifyNotDuplicateOrder
from responses import error, sucess


app = Flask(__name__)


def getErrorResponse(message):
    jsonResponse = app.response_class(
        response=error(message),
        status=400,
        mimetype="application/json"
    )
    return jsonResponse


def getSucesfullResponse(message):
    jsonResponse = app.response_class(
        response=sucess(message),
        status=200,
        mimetype="application/json"
    )
    return jsonResponse
 

def buysellShare(id, order):
    print(id)
    account = getAccount(id)
    print(account)
    if account is not None:
        if account["cash"]+(abs(order["total_shares"])*order["share_price"])>=0:
            if verifyNotDuplicateOrder(account["id"],order):
                if buySellIssuer(account["id"],order):
                    updateAccount(account,order)
                    return getSucesfullResponse(getAccountIssuers(account["id"]))
                else:
                    raise GBMException(constants.ERROR_STOCKS)
            else:
                raise GBMException(constants.ERROR_DUPLICATE_ORDER)
        else:
            raise GBMException(constants.ERROR_CASH)
    else:
        raise GBMException(constants.ERROR_ID)


@app.route("/accounts/<id>/orders", methods=["POST"])
def postOrders(id):
    try:             
        if(request.headers["Content-Type"] == "application/json"):
            order = request.json
            if order != None:
                if "timestamp" in order and "operation" in order and "issuer_name" in order and "total_shares" in order and "share_price" in order:
                    if order["operation"] in constants.OPERATION_TYPE and order["total_shares"]>0 and order["share_price"]>0:
                        day =datetime.fromtimestamp(order["timestamp"]).day
                        IST = pytz.timezone('America/Mexico_City')
                        today = datetime.now(IST).day
                        if day==today:
                            hour=datetime.fromtimestamp(order["timestamp"]).hour
                            if hour > 6 and hour<15:
                                if order["operation"]=="BUY":
                                    order["share_price"]=order["share_price"]*-1
                                    return buysellShare(id,order)
                                elif order["operation"]=="SELL":
                                    order["total_shares"]=order["total_shares"]*-1
                                    return buysellShare(id,order)
                                else:
                                    raise GBMException(constants.ERROR_OPERATION)  
                            raise GBMException(constants.ERROR_HOURS)  
                        raise GBMException(constants.ERROR_DAYS)  
                    raise GBMException(constants.ERROR_CASH)
                raise GBMException(constants.ERROR_REQUEST)
            raise GBMException(constants.ERROR_REQUEST)
        raise GBMException(constants.ERROR_REQUEST)
    except GBMException as error:
        return getErrorResponse(error)
    except BaseException as error:
        return getErrorResponse(error)

        
if __name__ == "__main__":
     app.run(host="0.0.0.0", port=8080)

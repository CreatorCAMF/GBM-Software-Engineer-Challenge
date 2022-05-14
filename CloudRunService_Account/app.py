import constants
from flask import Flask, request
from exceptions import GBMException
from accounts import createAccount
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


@app.route('/accounts', methods=['POST'])
def consultaSaldo():
    try:             
        if(request.headers['Content-Type'] == 'application/json'):
            content = request.json
            if content != None:
                if "cash" in content:
                    if content["cash"]>0:
                        return getSucesfullResponse(createAccount(content["cash"]))
                    raise GBMException(constants.ERROR_CASH)
                raise GBMException(constants.ERROR_REQUEST)
            raise GBMException(constants.ERROR_REQUEST)
        raise GBMException(constants.ERROR_REQUEST)
    except GBMException as error:
        return getErrorResponse(error)
    except BaseException as error:
        return getErrorResponse(error)

        
if __name__ == '__main__':
     app.run(host='0.0.0.0', port=8080)


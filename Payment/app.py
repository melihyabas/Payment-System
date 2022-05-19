import enum

from flask import request, Flask, jsonify
from datetime import date
# import libraries
app = Flask(__name__)


class CurrencyCode(enum.Enum): # Currency enum class
    TRY = "TRY"
    USD = "USD"
    EUR = "EUR"

class AccountType(enum.Enum): # Account Type enum class
    individual = "individual"
    corporate = "corporate"

class TransactionType(enum.Enum): # Transaction Type enum class
    payment = "payment"
    deposit = "deposit"
    withdraw = "withdraw"


accountList = dict() # keep accounts
transactions = dict() # keep transactions

@app.route('/')
def main_page():
    response = jsonify({"message": "main page of backend"})
    response.status_code = 200
    return response


@app.route('/account', methods=['POST'])
def create_account(): # creates a new account
    _json = request.json


    if 'accountNumber' not in _json or 'currencyCode' not in _json or 'ownerName' not in _json or 'accountType' not in _json:
        response = jsonify({'message': 'Bad Request - lack of parameters'})
        response.status_code = 400
        return response # lack of parameters

    _accountNumber = _json['accountNumber']
    _currencyCode = _json['currencyCode']
    _ownerName = _json['ownerName']
    _accountType = _json['accountType']

    if _accountNumber and _currencyCode and _ownerName and _accountType:
        if not isinstance(_accountNumber, int): # account number has to be integer
            response = jsonify({'message': 'Bad Request - invalid account number'})
            response.status_code = 400
            return response

        if _currencyCode not in CurrencyCode._value2member_map_: # currency code has to be enum type
            response = jsonify({'message': 'Bad Request - invalid currency code'})
            response.status_code = 400
            return response

        if _accountType not in AccountType._value2member_map_: #  account type has to be enum type
            response = jsonify({'message': 'Bad Request - invalid account type'})
            response.status_code = 400
            return response

        if accountList.get(_accountNumber): # if account is already exists
            response = jsonify({'message': 'Error - This account is already exists.'})
            response.status_code = 400
            return response

        accountJson = {
                "accountNumber":_accountNumber,
                "currencyCode": _currencyCode,
                "ownerName": _ownerName,
                "accountType": _accountType,
                "balance": 0
        } # account json file

        accountList[_accountNumber] = accountJson
        transactions[_accountNumber] = list()

        response = jsonify({'message': 'Account Succesfully created', 'account:': accountJson})

        response.status_code = 201 # created account
        return response

    else:
        response = jsonify({'message': 'Bad Request - invalid credentials'})
        response.status_code = 400
        return response


@app.route('/account', methods=['GET'])
def accountinfo():
    accountNumber = request.args.get('accountNumber')

    if accountNumber is None: # no account number
        response = jsonify({'message': 'Bad Request - no account number'})
        response.status_code = 400
        return response

    if not accountNumber.isdigit(): # account number must be integer
        response = jsonify({'message': 'Bad Request - invalid account number'})
        response.status_code = 400
        return response

    accountNumber = int(accountNumber)
    userInfo = accountList.get(accountNumber)

    if userInfo:
        response = jsonify(accountList.get(accountNumber))
        response.status_code = 200
        return response
    else:
        response = jsonify({'message': 'This account does not exist.'})
        response.status_code = 400
        return response

@app.route('/payment', methods=['POST'])
def payment(): # payment from an individual to corporate
    _json = request.json

    if 'senderAccount' not in _json or 'receiverAccount' not in _json or 'amount' not in _json:
        response = jsonify({'message': 'Bad Request - lack of parameters'})
        response.status_code = 400 # lack of parameters
        return response

    _senderAccount = _json['senderAccount']
    _receiverAccount = _json['receiverAccount']
    _amount = _json['amount']



    if not isinstance(_amount, float) and not isinstance(_amount, int):
        response = jsonify({'message': 'Bad Request - invalid amount'})
        response.status_code = 400 # amount must be number
        return response

    if not isinstance(_senderAccount, int):
        response = jsonify({'message': 'Bad Request - invalid senderAccount'})
        response.status_code = 400 # account number must be an integer
        return response

    if not isinstance(_receiverAccount, int):
        response = jsonify({'message': 'Bad Request - invalid receiverAccount'})
        response.status_code = 400 # account number must be an integer
        return response

    if not _senderAccount in accountList:
        response = jsonify({'message': 'Bad Request - senderAccount does not exist'})
        response.status_code = 400
        return response

    if not _receiverAccount in accountList:
        response = jsonify({'message': 'Bad Request - receiverAccount does not exist'})
        response.status_code = 400
        return response

    if(accountList.get(_senderAccount)['accountType'] == AccountType("individual").name and
            accountList.get(_receiverAccount)['accountType'] == AccountType("corporate").name):


        if accountList[_senderAccount]['balance'] < _amount:
            response = jsonify({'message': 'The account balance is not sufficient to send money.'})
            response.status_code = 400
            return response


        accountList[_senderAccount]['balance'] = round(accountList[_senderAccount]['balance'] - _amount, 2)
        accountList[_receiverAccount]['balance'] = round(accountList[_receiverAccount]['balance'] + _amount, 2)

        transactionJson = {
            "amount": _amount,
            "transactionType": TransactionType.payment.value,
            "accountNumber": _senderAccount,
            "createdAt": date.today()
        }
        transactions[_senderAccount].insert(0,transactionJson)

        transactionJson = {
            "amount": _amount,
            "transactionType": TransactionType.payment.value,
            "accountNumber": _receiverAccount,
            "createdAt": date.today()
        }
        transactions[_receiverAccount].insert(0,transactionJson)


    else:
        response = jsonify({'message': 'Payments can only be wired from an individual account to a corporate account.'})
        response.status_code = 400
        return response

    response = jsonify({'message': 'Payment done successfully.'})
    response.status_code = 200
    return response

@app.route('/deposit', methods=['POST'])
def deposit():
    _json = request.json

    if 'accountNumber' not in _json or 'amount' not in _json:
        response = jsonify({'message': 'Bad Request - lack of parameters'})
        response.status_code = 400
        return response

    _accountNumber = _json['accountNumber']
    _amount = _json['amount']

    if _accountNumber and _amount:

        if not isinstance(_accountNumber, int):
            response = jsonify({'message': 'Bad Request - invalid accountNumber'})
            response.status_code = 400 # account number must be an integer
            return response

        if not isinstance(_amount, float) and not isinstance(_amount, int):
            response = jsonify({'message': 'Bad Request - invalid amount'})
            response.status_code = 400 # amount must be a number
            return response

        if not _accountNumber in accountList:
            response = jsonify({'message': 'Bad Request - account does not exist'})
            response.status_code = 400 # account does not exist
            return response

        if accountList.get(_accountNumber)['accountType'] == AccountType("individual").name:

            accountList[_accountNumber]['balance'] = round(accountList[_accountNumber]['balance'] + _amount, 2)

            transactionJson = {
                "amount": round(_amount,2),
                "transactionType": TransactionType.deposit.value,
                "accountNumber": _accountNumber,
                "createdAt": date.today()
            }
            transactions[_accountNumber].insert(0, transactionJson)
            print(transactionJson)
            response = jsonify({'message': 'deposit operation done successfully.'})
            response.status_code = 200
            return response
        else:
            response = jsonify({'message': 'Only individual accounts can deposit or withdraw money.'})
            response.status_code = 400
            return response
    else:
        response = jsonify({'message': 'Bad Request - invalid credentials'})
        response.status_code = 400
        return response

@app.route('/withdraw', methods=['POST'])
def withdraw():
    _json = request.json

    if 'accountNumber' not in _json or 'amount' not in _json:
        response = jsonify({'message': 'Bad Request - lack of parameters'})
        response.status_code = 400
        return response

    _accountNumber = _json['accountNumber']
    _amount = _json['amount']

    if _accountNumber and _amount:
        # account number must be an integer
        if not isinstance(_accountNumber, int):
            response = jsonify({'message': 'Bad Request - invalid accountNumber'})
            response.status_code = 400
            return response

        if not isinstance(_amount, float) and not isinstance(_amount, int):
            response = jsonify({'message': 'Bad Request - invalid amount'})
            response.status_code = 400
            return response

        if not _accountNumber in accountList:
            response = jsonify({'message': 'Bad Request - account does not exist'})
            response.status_code = 400
            return response

        if accountList.get(_accountNumber)['accountType'] == AccountType("individual").name:
            # account type must be in enum class
            if accountList[_accountNumber]['balance'] < _amount:
                response = jsonify({'message': 'The account balance is not sufficient to withdraw money.'})
                response.status_code = 400
                return response

            accountList[_accountNumber]['balance'] = round(accountList[_accountNumber]['balance'] - _amount,2)

            transactionJson = {
                "amount": _amount,
                "transactionType": TransactionType.withdraw.value,
                "accountNumber": _accountNumber,
                "createdAt": date.today()
            }
            transactions[_accountNumber].insert(0, transactionJson)

            response = jsonify({'message': 'Withdraw operation done successfully.'})
            response.status_code = 200
            return response
        else:
            response = jsonify({'message': 'Only individual accounts can deposit or withdraw money.'})
            response.status_code = 400
            return response
    else:
        response = jsonify({'message': 'Bad Request - invalid credentials'})
        response.status_code = 400
        return response


@app.route('/accounting', methods=['GET'])
def transactionHistory(): # returns history of an account
    _accountNumber = request.args.get('accountNumber')

    if _accountNumber is None:
        response = jsonify({'message': 'Bad Request - no account number'})
        response.status_code = 400
        return response

    if not _accountNumber.isdigit(): # account number must be an integer
        response = jsonify({'message': 'Bad Request - invalid account number'})
        response.status_code = 400
        return response

    _accountNumber = int(_accountNumber)
    userInfo = accountList.get(_accountNumber)
    if not userInfo:
        print(_accountNumber)
        print(accountList)
        response = jsonify({'message': 'Bad Request - account does not exist'})
        response.status_code = 400
        return response

    return jsonify(transactions[_accountNumber]) # return all history

def createSomeAccounts(): # a helper function to create some users

    currencyCode = "TRY"
    ownerName = "name"
    accountType = "individual"

    for i in range(3):
        if i%2 == 0:
            accountType = "individual"
        else:
            accountType = "corporate"

        name = ownerName+str(i)

        userjson = {
            "accountNumber": i,
            "currencyCode": currencyCode,
            "ownerName": name,
            "accountType": accountType,
            "balance": 0
        }
        accountList[i] = userjson
        transactions[i] = list()





if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)

createSomeAccounts()

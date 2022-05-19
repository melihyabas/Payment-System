# Payment System Backend

This is a payment rest api that allows users to create an account (both individual or corporate), deposit/withdraw money and make a payment.

Only individual accounts can deposit or withdraw money. 
Payments can only be wired from an individual account to a corporate account.

Each money transaction creates an accounting with transaction amount, transaction type
and account information. These transactions are able to be listed as accounting history.

All accounts and accounting id held in memory, so there is no database.

## How to Run This Project?

This is a dockerized project.

* Clone this project into your local machine.

* Install Docker software and open it.
* Open the project with an ide like PyCharm, VsCode etc.

* Open terminal type these commands and press enter;
```
cd Payment
```
```
docker-compose up
```

This is all. Thank you.

You can use 'Tringle.postman_collection.json' file to test apis in Postman.

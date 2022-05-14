# GBM Software Engineer Challenge

## Bussines Rules
* Insufficient Balance
* Insufficient Stocks
* Duplicated Operation
* Closed Market
* Other invalid operations (not described in challenge) or considerations:
    * Account must be created with cash > 0
    * Operation not specified will be discarded
    * Operations can only be acepted if the timespan is the sameday
    * Timezone is America/Mexico City
    * If an acount has some stocks and a new order arrive to buy more the total_share is added, and the share_price is updated to the new one.
    

# _Solution_


* [Project GCP](#GCP-Project)
* [Service Account](#service-account)
* [Variables ](#variables)
* [Firestore](#Firestore)
* [Pipelines](#Pipelines)
* [Apigee](#Apigee)
* [Contact](#Contact)


## GCP Project

In the first step we must to create a GCP Project in https://console.cloud.google.com

It is important to remember de project id because it will be requires in the next steps, for this challenge the project id is gbm-challenge-backend

![GCP Project](./Img/CreateProject.png)

Its time to enable our first APIs:

![GCP Project](./Img/EnableFirstApis.png)

![GCP Project](./Img/EnableApi.png)

![GCP Project](./Img/CloudBuild.png)


## Service Account

A service account is needed to execute some task, to create it follow the next steps:

![Service Account ](./Img/ServiceAcount.png)

![Service Account ](./Img/ServiceAcountCreate.png)

![Service Account ](./Img/ServiceAcountCreate2.png)

![Service Account ](./Img/ServiceAcountCreatePermisos.png)

Note: For this challenge the service account has Owner privileges nevertheless this is not a secure practice, in a real PROD environment you must assign only the correct roles:

* Apigee API Admin
* Apigee Developer Admin
* Apigee Environment Admin
* Cloud Build Editor
* Service Account User
* Cloud Run Admin

In the other hand it is important to remember the service account "mail" because it will be used in the next steps, in this case the value is gbm-challenge-backend@gbm-challenge-backend.iam.gserviceaccount.com


## Project Variables

In some files (cloudbuild.yaml) exists variables that will be replace with build pipelines, so you must change these values with yours.

```
_PROJECT_ID=gbm-challenge-backend
_REGION=us-east4
_SERVICE_ACCOUNT=gbm-challenge-backend@gbm-challenge-backend.iam.gserviceaccount.com
```

## Firestore

To store the data we will use Firestore, the next steps will let you create the db, collections and indexes required to run the services.

### DB

![Firestore](./Img/SelectFirestore.png)

![Firestore](./Img/SelectFirestoreOption.png)

![Firestore](./Img/SelectFirestoreRegion.png)

### Collections

![Firestore](./Img/CrearColeccion.png)

![Firestore](./Img/CrearColeccionAccounts.png)

![Firestore](./Img/CrearColeccionIssuers.png)

![Firestore](./Img/CrearColeccionOrders.png)

By default firestore add a document when you create the collection nevertheless those collections are not required, deleted them is opcional.

### Indexes

To perform compound queries some indexes are required:

![Firestore](./Img/CrearIndiceIssuers.png)

![Firestore](./Img/CrearIndiceOrders.png)

	
## Pipelines

### Cloud Build

It is time to create the triggers that will execute our pipelines and link it with our github repository, in this way every time we make a push the trigger will run the pipeline.

Note: You can run them manually using the run option.

![Pipelines](./Img/CloudBuildTrigger.png)

![Pipelines](./Img/CloudBuildTrigger1.png)

![Pipelines](./Img/CloudBuildTrigger2.png)

![Pipelines](./Img/CloudBuildTrigger3.png)

![Pipelines](./Img/CloudBuildTrigger4.png)

![Pipelines](./Img/CloudBuildTrigger5.png)

It is important enable some roles before run the pipeline:

![Pipelines](./Img/CloudBuildTriggerRoles.png)

Now you can run them whenever you want:

![Pipelines](./Img/CloudBuildTriggerRun.png)

### Cloud Run 

Now its time to go to Cloud Run to see our services:

* service-accounts
* service-orders

![CloudRun](./Img/CloudRun.png)

You can click in one service to see its information (including the URL)

![CloudRun](./Img/CloudRun1.png)

At this moment you will not be able to make a succesfull request cause our pipeline set them as private resources to increse the security, but you can set them as public resources to test them:

![CloudRun](./Img/CloudRunPublic.png)


## Apigee

Other persons maybe let the challenge there but not me, to garantee security and be able to test Apigee was implementet as is shown in the next diagram

![Apigee](./Img/Diagram.png)

The files to build the proxy are in the folder Apigee ![Apigee](./Apigee/GBM-Software-Engineer-Challenge.zip)

The postman collection to test the services is in  ![PostMan](./Postman/GBM.postman_collection.json)

The Swagger is in this repository or can be consulted in the [Web Portal] (https://tobyobito-eval-gbmaccount.apigee.io/docs/gbm/1/overview)

![Swagger](./Img/Swagger.png)


## Contact

I will be glad to answer your questions

Mail: camtzf@outlook.com.mx
Phone: 722-510-10-52
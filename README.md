# Receipt Processor
The aim of this python application is to process receipts and calculate points for the receipts using specified rules. <br>
The application provides two endpoints:
- **Process Receipts**: Accepts a JSON receipt and returns a unique identifier for the receipt.
- **Get Points**: Retrieves the points awarded to a receipt using its unique identifier.

## Features
- FastAPI-based RESTful service
- Interactive API documentation at `/docs`
- Local and Dockerized deployment options

## Local Setup
The application uses **FastAPI**, a modern Python web framework. Follow the steps below to set up the application on your local system.

### Prerequisites
- Python 3.7 or higher (The application as developed using Python 3.11)
- `pip` (Python package manager)

### Create a Virtual Environment
To isolate dependencies, create a virtual environment using command `python -m venv .venv` and activate it.

### Install Dependencies
Install the required packages listed in requirements.txt using command `pip install requirements.txt`

### Run the Application
To start the application on development mode use command `fastapi dev FetchApp/receipt_service.py` <br>
To start the application on production mode, use command `fastapi run FetchApp/receipt_service.py`

### Test the Application
By default, the application runs on `http://127.0.0.1:8000` <br>
The interactive API docs can be found at `http://127.0.0.1:8000/docs` <br>

The application can also be tested using curl commands. For example: <br>
Process Receipt:
```
curl -X POST "http://127.0.0.1:8000/receipts/process" \
-H "Content-Type: application/json" \
-d '{
  "retailer": "Target",
  "purchaseDate": "2022-01-01",
  "purchaseTime": "13:01",
  "items": [
    {
      "shortDescription": "Mountain Dew 12PK",
      "price": "6.49"
    },{
      "shortDescription": "Emils Cheese Pizza",
      "price": "12.25"
    },{
      "shortDescription": "Knorr Creamy Chicken",
      "price": "1.26"
    },{
      "shortDescription": "Doritos Nacho Cheese",
      "price": "3.35"
    },{
      "shortDescription": "   Klarbrunn 12-PK 12 FL OZ  ",
      "price": "12.00"
    }
  ],
  "total": "35.35"
}'
```

Get Points:
```
curl -X GET "http://127.0.0.1:8000/receipts/{id}/points"
```

## Containerized Setup
For a more robust deployment, you can (and should) run the application in a Docker container. <br>
The following steps help to set up the application in containerized environment:

### Prerequisites
- Docker

### Create Dockerfile
The first step is to create a Dockerfile (if not present), that provides a blueprint on how the Docker image is created. <br>
For this application, Dockerfile is already created.

### Build Image
Build the Docker image for the application using the command `docker build -t fetch-app .`

### Run Container
Spin up a Docker container using the created image using the command `docker run -d --name fetch-app-container -p 8000:8000 fetch-app`

### Test the Application
Access the application running in the container:
- Localhost URL: http://127.0.0.1:8000
- Interactive API Documentation: http://127.0.0.1:8000/docs

The application can also be tested using curl commands. For example: <br>
Process Receipt:
```
curl -X POST "http://127.0.0.1:8000/receipts/process" \
-H "Content-Type: application/json" \
-d '{
  "retailer": "Target",
  "purchaseDate": "2022-01-01",
  "purchaseTime": "13:01",
  "items": [
    {
      "shortDescription": "Mountain Dew 12PK",
      "price": "6.49"
    },{
      "shortDescription": "Emils Cheese Pizza",
      "price": "12.25"
    },{
      "shortDescription": "Knorr Creamy Chicken",
      "price": "1.26"
    },{
      "shortDescription": "Doritos Nacho Cheese",
      "price": "3.35"
    },{
      "shortDescription": "   Klarbrunn 12-PK 12 FL OZ  ",
      "price": "12.00"
    }
  ],
  "total": "35.35"
}'
```

Get Points:
```
curl -X GET "http://127.0.0.1:8000/receipts/{id}/points"
```

### Stopping the Container
Stop the running container using using command `docker stop fetch-app-container` which also terminates the running application.
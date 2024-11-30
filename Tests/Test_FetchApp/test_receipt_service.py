from fastapi.testclient import TestClient
from FetchApp.receipt_service import app, calculate_points, Receipt
import copy

client = TestClient(app)

# Mock receipt object with valid data to be used in tests
mock_valid_receipt = {
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
}

def test_process_receipt_valid_data():
    """
    Test the /receipts/process endpoint with valid receipt data.
    Ensures the response contains a 200 status and an ID field.
    """
    response = client.post("/receipts/process", json=mock_valid_receipt)
    assert response.status_code == 200
    assert "id" in response.json()

def test_process_receipt_invalid_data_retailer():
    """
    Test /receipts/process with invalid retailer data.
    Ensures the endpoint rejects empty or malformed retailer names.
    """
    invalid_receipt = mock_valid_receipt.copy()
    invalid_receipt["retailer"] = ""
    response = client.post("/receipts/process", json=invalid_receipt)
    assert response.status_code == 422

    invalid_receipt = mock_valid_receipt.copy()
    invalid_receipt["retailer"] = "Target@123"
    response = client.post("/receipts/process", json=invalid_receipt)
    assert response.status_code == 422

def test_process_receipt_invalid_data_purchaseDate():
    """
    Test /receipts/process with invalid purchase dates.
    Ensures the endpoint rejects missing or invalid dates.
    """
    invalid_receipt = mock_valid_receipt.copy()
    invalid_receipt["purchaseDate"] = ""
    response = client.post("/receipts/process", json=invalid_receipt)
    assert response.status_code == 422

    invalid_receipt = mock_valid_receipt.copy()
    invalid_receipt["purchaseDate"] = "2022-31-12"
    response = client.post("/receipts/process", json=invalid_receipt)
    assert response.status_code == 422

def test_process_receipt_invalid_data_purchaseTime():
    """
    Test /receipts/process with invalid purchase dates.
    Ensures the endpoint rejects missing or invalid dates.
    """
    invalid_receipt = mock_valid_receipt.copy()
    invalid_receipt["purchaseTime"] = ""
    response = client.post("/receipts/process", json=invalid_receipt)
    assert response.status_code == 422

    invalid_receipt = mock_valid_receipt.copy()
    invalid_receipt["purchaseTime"] = "25:01"
    response = client.post("/receipts/process", json=invalid_receipt)
    assert response.status_code == 422

def test_process_receipt_invalid_data_items():
    """
    Test /receipts/process with invalid items data.
    Ensures the endpoint rejects empty or invalid items list.
    """
    invalid_receipt = copy.deepcopy(mock_valid_receipt) # Deep copy is required because Nested Objects are modified in shallow copy
    invalid_receipt["items"] = []
    response = client.post("/receipts/process", json=invalid_receipt)
    assert response.status_code == 422
    
    invalid_receipt = copy.deepcopy(mock_valid_receipt)
    invalid_receipt["items"][0]["shortDescription"] = ""
    response = client.post("/receipts/process", json=invalid_receipt)
    assert response.status_code == 422

    invalid_receipt = copy.deepcopy(mock_valid_receipt)
    invalid_receipt["items"][0]["price"] = ""
    response = client.post("/receipts/process", json=invalid_receipt)
    assert response.status_code == 422

    invalid_receipt = copy.deepcopy(mock_valid_receipt)
    invalid_receipt["items"][0]["price"] = "-1.20"
    response = client.post("/receipts/process", json=invalid_receipt)
    assert response.status_code == 422

    invalid_receipt = copy.deepcopy(mock_valid_receipt)
    invalid_receipt["items"][0]["price"] = "randomString"
    response = client.post("/receipts/process", json=invalid_receipt)
    assert response.status_code == 422

def test_process_receipt_invalid_data_Total():
    """
    Test /receipts/process with invalid total values.
    Ensures the endpoint rejects missing, or invalid totals.
    """
    invalid_receipt = mock_valid_receipt.copy()
    invalid_receipt["total"] = ""
    response = client.post("/receipts/process", json=invalid_receipt)
    assert response.status_code == 422

    invalid_receipt = mock_valid_receipt.copy()
    invalid_receipt["total"] = "-5.00"
    response = client.post("/receipts/process", json=invalid_receipt)
    assert response.status_code == 422

    invalid_receipt = mock_valid_receipt.copy()
    invalid_receipt["total"] = "randomString"
    response = client.post("/receipts/process", json=invalid_receipt)
    assert response.status_code == 422

def test_get_points_success():
    """
    Test the /receipts/{id}/points endpoint with a valid receipt ID.
    Ensures the endpoint returns the correct points for the receipt.
    """
    process_response = client.post("/receipts/process", json=mock_valid_receipt)
    receipt_id = process_response.json()["id"]

    points_response = client.get(f"/receipts/{receipt_id}/points")
    assert points_response.status_code == 200
    assert "points" in points_response.json()

def test_get_points_invalid_id():
    """
    Test the /receipts/{id}/points endpoint with an invalid receipt ID.
    Ensures the endpoint returns a 404 error with relevant message.
    """
    response = client.get("/receipts/nonexistent-id/points")
    assert response.status_code == 404
    assert response.json()["detail"] == "No receipt found for that id"

def test_calculate_points():
    """
    Test the calculate_points function with valid receipt data.
    Ensures the function returns a valid result.
    """
    receipt = Receipt(**mock_valid_receipt)
    points = calculate_points(receipt)
    assert isinstance(points, int)
    assert points > 0
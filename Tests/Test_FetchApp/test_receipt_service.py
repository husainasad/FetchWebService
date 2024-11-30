from fastapi.testclient import TestClient
from FetchApp.receipt_service import app, calculate_points, Receipt
import copy

client = TestClient(app)

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
    response = client.post("/receipts/process", json=mock_valid_receipt)
    assert response.status_code == 200
    assert "id" in response.json()

def test_process_receipt_invalid_data_retailer():
    invalid_receipt = copy.deepcopy(mock_valid_receipt)
    invalid_receipt["retailer"] = ""
    response = client.post("/receipts/process", json=invalid_receipt)
    assert response.status_code == 422

    invalid_receipt = copy.deepcopy(mock_valid_receipt)
    invalid_receipt["retailer"] = "Target@123"
    response = client.post("/receipts/process", json=invalid_receipt)
    assert response.status_code == 422

def test_process_receipt_invalid_data_purchaseDate():
    invalid_receipt = copy.deepcopy(mock_valid_receipt)
    invalid_receipt["purchaseDate"] = ""
    response = client.post("/receipts/process", json=invalid_receipt)
    assert response.status_code == 422

    invalid_receipt = copy.deepcopy(mock_valid_receipt)
    invalid_receipt["purchaseDate"] = "2022-31-12"
    response = client.post("/receipts/process", json=invalid_receipt)
    assert response.status_code == 422

def test_process_receipt_invalid_data_purchaseTime():
    invalid_receipt = copy.deepcopy(mock_valid_receipt)
    invalid_receipt["purchaseTime"] = ""
    response = client.post("/receipts/process", json=invalid_receipt)
    assert response.status_code == 422

    invalid_receipt = copy.deepcopy(mock_valid_receipt)
    invalid_receipt["purchaseTime"] = "25:01"
    response = client.post("/receipts/process", json=invalid_receipt)
    assert response.status_code == 422

def test_process_receipt_invalid_data_items():
    invalid_receipt = copy.deepcopy(mock_valid_receipt)
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
    invalid_receipt = copy.deepcopy(mock_valid_receipt)
    invalid_receipt["total"] = ""
    response = client.post("/receipts/process", json=invalid_receipt)
    assert response.status_code == 422

    invalid_receipt = copy.deepcopy(mock_valid_receipt)
    invalid_receipt["total"] = "-5.00"
    response = client.post("/receipts/process", json=invalid_receipt)
    assert response.status_code == 422

    invalid_receipt = copy.deepcopy(mock_valid_receipt)
    invalid_receipt["total"] = "randomString"
    response = client.post("/receipts/process", json=invalid_receipt)
    assert response.status_code == 422

def test_get_points_success():
    process_response = client.post("/receipts/process", json=mock_valid_receipt)
    receipt_id = process_response.json()["id"]

    points_response = client.get(f"/receipts/{receipt_id}/points")
    assert points_response.status_code == 200
    assert "points" in points_response.json()

def test_get_points_invalid_id():
    response = client.get("/receipts/nonexistent-id/points")
    assert response.status_code == 404
    assert response.json()["detail"] == "No receipt found for that id"

def test_calculate_points():
    receipt = Receipt(**mock_valid_receipt)
    points = calculate_points(receipt)
    assert isinstance(points, int)
    assert points > 0
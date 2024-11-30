from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel, Field, model_validator
from uuid import uuid4
from typing import List, Dict
import math
from datetime import date, time
from decimal import Decimal

app = FastAPI()

# Constants for Points Calculation
AFTERNOON_START = time(14, 0) # 2:00 PM
AFTERNOON_END = time(16, 0) # 4:00 PM
PRICE_MULTIPLIER = Decimal("0.2") # Item Price multiplier

# Data Model for Individual Item
class Item(BaseModel):
    """
    Represents an item on the receipt with details including
    its short description and price.
    """
    shortDescription: str = Field(
        ..., 
        pattern = "^[\\w\\s\\-]+$", 
        description="The Short Product Description for the item.", 
        json_schema_extra={"example": "Mountain Dew 12PK"}
    )
    price: str = Field(
        ..., 
        pattern = "^\\d+\\.\\d{2}$", 
        description="The total price payed for this item.", 
        json_schema_extra={"example": "6.49"}
    )

# Data Model for Receipt
class Receipt(BaseModel):
    """
    Represents a receipt submitted for processing, including
    retailer details, purchase date,time, items, and total price.
    """
    retailer: str = Field(
        ..., 
        pattern = "^[\\w\\s\\-&]+$", 
        description="The name of the retailer or store the receipt is from.", 
        json_schema_extra={"example": "Target"}
    )
    purchaseDate: date = Field(
        ..., 
        description="The date of the purchase printed on the receipt.", 
        json_schema_extra={"example": "2022-01-01"}
    )
    purchaseTime: time = Field(
        ..., 
        description="The time of the purchase printed on the receipt. 24-hour time expected.", 
        json_schema_extra={"example": "13:01"}
    )
    items: List[Item] = Field(
        ..., 
        min_length=1, 
        description="List of items purchased"
    )
    total: str = Field(
        ..., 
        pattern = "^\\d+\\.\\d{2}$", 
        description="The total amount paid on the receipt.", 
        json_schema_extra={"example": "35.35"}
    )

    @model_validator(mode="after")
    def validate_total_matches_items(cls, values):
        """
        Validates that the total matches the sum of the item prices.
        """
        items = values.items
        total = values.total

        sum_of_prices = sum(Decimal(item.price) for item in items)

        if sum_of_prices != Decimal(total):
            raise ValueError(f"Total {total} does not match the sum of individual item prices, {sum_of_prices}.")

        return values

# Response Model for Receipt Processing API
class ReceiptResponse(BaseModel):
    """
    Response containing the ID assigned to a processed receipt.
    """
    id: str = Field(
        ..., pattern = "^\\S+$", 
        description="Returns the ID assigned to the receipt", 
        json_schema_extra={"example": "adb6b560-0eef-42bc-9d16-df48f30e89b2"}
    )

# Response Model for Get Points API
class PointsResponse(BaseModel):
    """
    Response containing the number of points awarded for a receipt.
    """
    points: int = Field(
        ..., 
        description="The number of points awarded", 
        json_schema_extra={"example": 100}
    )

# Function to calculate points for a receipt based on specified rules
def calculate_points(receipt: Receipt) -> int:
    """
    Calculate points for a receipt using various rules
    """
    points = 0

    # Rule 1: One point for every alphanumeric character in the retailer name
    points += sum(1 for char in receipt.retailer if char.isalnum())

    # Rule 2: 50 points if the total is a round dollar amount with no cents
    total = Decimal(receipt.total)

    if total % 1 == 0:
        points += 50

    # Rule 3: 25 points if the total is a multiple of 0.25
    if total % Decimal("0.25") == 0:
        points += 25

    # Rule 4: 5 points for every two items on the receipt
    points += (len(receipt.items) // 2) * 5

    # Rule 5: Points for item descriptions whose trimmed length is a multiple of 3
    for item in receipt.items:
        trimmed_length = len(item.shortDescription.strip())
        item_price = Decimal(item.price)
        if trimmed_length % 3 == 0:
            points += math.ceil(item_price * PRICE_MULTIPLIER)

    # Rule 6: 6 points if the day in the purchase date is odd
    if receipt.purchaseDate.day % 2 != 0:
        points += 6

    # Rule 7: 10 points if the time of purchase is after 2:00pm and before 4:00pm
    if AFTERNOON_START <= receipt.purchaseTime < AFTERNOON_END:
        points += 10

    return points

# In-memory databases to store receipt and points data
receipts_db: Dict[str, Receipt] = {}
points_db: Dict[str, int] = {}

# Process Receipt Endpoint
@app.post("/receipts/process", response_model=ReceiptResponse, status_code=200)
async def process_receipt(receipt: Receipt):
    """
    Endpoint to process a receipt. Assigns a unique ID, calculates points,
    and stores the receipt and points data in in-memory databases.
    """ 
    receipt_id = str(uuid4())
    receipts_db[receipt_id] = receipt.model_dump()
    points_db[receipt_id] = calculate_points(receipt)

    return {"id": receipt_id}

# Get Points Endpoint
@app.get("/receipts/{id}/points", response_model=PointsResponse, status_code=200)
async def get_points(id: str = Path(..., pattern = "^\\S+$", description="Receipt ID")):
    """
    Endpoint to retrieve points awarded for a receipt using its unique ID.
    Returns 404 error if no receipt is found for the given ID.
    """
    id = id.strip('"')

    if id not in points_db:
        raise HTTPException(status_code=404, detail="No receipt found for that id")
    
    points = points_db[id]

    return {"points": points}
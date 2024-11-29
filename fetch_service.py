from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel, Field, field_validator, ValidationInfo
from uuid import uuid4
from typing import List, Dict
import math
from datetime import datetime
from decimal import Decimal, InvalidOperation

app = FastAPI()

AFTERNOON_START = datetime.strptime("14:00", "%H:%M").time()
AFTERNOON_END = datetime.strptime("16:00", "%H:%M").time()
PRICE_MULTIPLIER = Decimal("0.2")

class Item(BaseModel):
    shortDescription: str = Field(..., description="Short description of the item")
    price: str = Field(..., description="Price of the item")

    @field_validator("price")
    def validate_price(cls, price_value):
        try:
            price = Decimal(price_value)
            if price < 0:
                # raise HTTPException(status_code=400, detail="Price must be greater than zero")
                raise ValueError("Price must be greater than zero")
            return price_value
        except InvalidOperation:
            # raise HTTPException(status_code=400, detail="Price must be a valid decimal number")
            raise ValueError("Price must be a valid decimal number")

class Receipt(BaseModel):
    retailer: str = Field(..., description="Name of the retailer")
    purchaseDate: str = Field(..., description="Purchase date in YYYY-MM-DD format")
    purchaseTime: str = Field(..., description="Purchase time in HH:MM format")
    items: List[Item] = Field(..., min_items=1, description="List of items purchased")
    total: str = Field(..., description="Total amount spent")

    @field_validator("purchaseDate")
    def validate_date(cls, purchaseDate_value):
        try:
            datetime.strptime(purchaseDate_value, "%Y-%m-%d")
            return purchaseDate_value
        except ValueError:
            # raise HTTPException(status_code=400, detail="purchaseDate must be a valid input of format YYYY-MM-DD")
            raise ValueError("purchaseDate must be a valid input of format YYYY-MM-DD")
        
    @field_validator("purchaseTime")
    def validate_time(cls, purchaseTime_value):
        try:
            datetime.strptime(purchaseTime_value, "%H:%M").time()
            return purchaseTime_value
        except ValueError:
            # raise HTTPException(status_code=400, detail="purchaseTime must be a valid input of 24 Hours format (HH:MM)")
            raise ValueError("purchaseTime must be a valid input of 24 Hours format (HH:MM)")
        
    @field_validator("total")
    def validate_total(cls, total_value, info: ValidationInfo) -> str:
        try:
            total = Decimal(total_value)
            items = info.data.get("items")
            if items is not None:
                calculated_total = sum(Decimal(item.price) for item in items)
                if total != calculated_total:
                    # raise HTTPException(status_code=400, detail=f"Total ({total}) does not match the sum of item prices ({calculated_total})")
                    raise ValueError(f"Total ({total}) does not match the sum of item prices ({calculated_total})")
            return total_value
        except InvalidOperation:
            # raise HTTPException(status_code=400, detail="Total must be a valid decimal number")
            raise ValueError("Total must be a valid decimal number")


class ReceiptResponse(BaseModel):
    id: str = Field(..., description="Unique ID assigned to the receipt")

class PointsResponse(BaseModel):
    points: int = Field(..., description="Points awarded for the receipt")

def calculate_points(receipt: Receipt) -> int:
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
    purchase_date = datetime.strptime(receipt.purchaseDate, "%Y-%m-%d")
    if purchase_date.day % 2 != 0:
        points += 6

    # Rule 7: 10 points if the time of purchase is after 2:00pm and before 4:00pm
    purchase_time = datetime.strptime(receipt.purchaseTime, "%H:%M").time()
    if AFTERNOON_START <= purchase_time < AFTERNOON_END:
        points += 10

    return points

receipts_db: Dict[str, Receipt] = {}
points_db: Dict[str, int] = {}

@app.post("/receipts/process", response_model=ReceiptResponse, status_code=200)
async def process_receipt(receipt: Receipt):
    receipt_id = str(uuid4())

    receipts_db[receipt_id] = receipt.model_dump()
    points_db[receipt_id] = calculate_points(receipt)

    return {"id": receipt_id}

@app.get("/receipts/{id}/points", response_model=PointsResponse, status_code=200)
async def get_points(id: str = Path(..., description="Receipt ID")):
    id = id.strip('"')

    if id not in points_db:
        raise HTTPException(status_code=404, detail="No receipt found for given id")
    
    points = points_db[id]

    return {"points": points}
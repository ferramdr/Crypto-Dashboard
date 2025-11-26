"""
FastAPI Application - Crypto Investment Tracker
Implements CQRS pattern: Writes to Master, Reads from Replica
"""
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
import requests
from datetime import datetime

from database import engine_master, get_db_write, get_db_read
from models import Base, Investment

# ============================================
# CREATE TABLES
# ============================================
# Create all tables in the master database
Base.metadata.create_all(bind=engine_master)

# ============================================
# FASTAPI APP INITIALIZATION
# ============================================
app = FastAPI(
    title="Crypto Investment Tracker",
    description="Sistema de seguimiento de inversiones en criptomonedas con replicación PostgreSQL",
    version="1.0.0"
)

# ============================================
# PYDANTIC SCHEMAS
# ============================================
class InvestmentCreate(BaseModel):
    """Schema for creating a new investment"""
    coin: str
    amount: float

    class Config:
        json_schema_extra = {
            "example": {
                "coin": "bitcoin",
                "amount": 0.5
            }
        }


class InvestmentResponse(BaseModel):
    """Schema for investment response"""
    id: int
    coin_name: str
    amount: float
    purchase_price_usd: float
    timestamp: datetime
    total_value_usd: float

    class Config:
        from_attributes = True


# ============================================
# HELPER FUNCTIONS
# ============================================
def get_crypto_price(coin_name: str) -> float:
    """
    Fetch current cryptocurrency price from CoinGecko API
    
    Args:
        coin_name: Name of the cryptocurrency (e.g., 'bitcoin', 'ethereum')
    
    Returns:
        Current price in USD
    
    Raises:
        HTTPException: If API call fails or coin not found
    """
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_name}&vs_currencies=usd"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if coin_name not in data:
            raise HTTPException(
                status_code=404,
                detail=f"Cryptocurrency '{coin_name}' not found. Please check the coin name."
            )
        
        price = data[coin_name]["usd"]
        return float(price)
    
    except requests.RequestException as e:
        raise HTTPException(
            status_code=503,
            detail=f"Failed to fetch cryptocurrency price: {str(e)}"
        )


# ============================================
# API ENDPOINTS
# ============================================

@app.get("/")
def read_root():
    """Root endpoint with API information"""
    return {
        "message": "Crypto Investment Tracker API",
        "version": "1.0.0",
        "endpoints": {
            "POST /invest": "Create a new investment (writes to Master DB)",
            "GET /history": "Get investment history (reads from Replica DB)",
            "GET /stats": "Get investment statistics"
        }
    }


@app.post("/invest", response_model=dict)
def create_investment(
    investment: InvestmentCreate,
    db: Session = Depends(get_db_write)
):
    """
    Create a new cryptocurrency investment.
    
    ⚠️ WRITES TO MASTER DATABASE (172.20.0.10)
    
    Args:
        investment: Investment details (coin and amount)
        db: Database session (Master)
    
    Returns:
        Confirmation with investment details
    """
    # Get current price from CoinGecko API
    current_price = get_crypto_price(investment.coin)
    
    # Calculate total investment value
    total_value = investment.amount * current_price
    
    # Create database record
    db_investment = Investment(
        coin_name=investment.coin,
        amount=investment.amount,
        purchase_price_usd=current_price
    )
    
    # Save to MASTER database
    db.add(db_investment)
    db.commit()
    db.refresh(db_investment)
    
    return {
        "status": "success",
        "message": "Investment saved to MASTER database",
        "database": "Master (172.20.0.10)",
        "investment": {
            "id": db_investment.id,
            "coin": db_investment.coin_name,
            "amount": db_investment.amount,
            "price_per_coin_usd": current_price,
            "total_value_usd": total_value,
            "timestamp": db_investment.timestamp.isoformat()
        }
    }


@app.get("/history", response_model=List[InvestmentResponse])
def get_investment_history(db: Session = Depends(get_db_read)):
    """
    Get all investment history.
    
    ✅ READS FROM REPLICA DATABASE (172.20.0.11)
    
    Args:
        db: Database session (Replica)
    
    Returns:
        List of all investments
    """
    investments = db.query(Investment).order_by(Investment.timestamp.desc()).all()
    
    # Calculate current total value for each investment
    response = []
    for inv in investments:
        total_value = inv.amount * inv.purchase_price_usd
        response.append(
            InvestmentResponse(
                id=inv.id,
                coin_name=inv.coin_name,
                amount=inv.amount,
                purchase_price_usd=inv.purchase_price_usd,
                timestamp=inv.timestamp,
                total_value_usd=total_value
            )
        )
    
    return response


@app.get("/stats")
def get_statistics(db: Session = Depends(get_db_read)):
    """
    Get investment statistics.
    
    ✅ READS FROM REPLICA DATABASE (172.20.0.11)
    
    Returns:
        Statistics about investments
    """
    investments = db.query(Investment).all()
    
    if not investments:
        return {
            "total_investments": 0,
            "total_value_usd": 0,
            "coins": []
        }
    
    total_value = sum(inv.amount * inv.purchase_price_usd for inv in investments)
    
    # Group by coin
    coins_summary = {}
    for inv in investments:
        if inv.coin_name not in coins_summary:
            coins_summary[inv.coin_name] = {
                "total_amount": 0,
                "total_value_usd": 0,
                "count": 0
            }
        coins_summary[inv.coin_name]["total_amount"] += inv.amount
        coins_summary[inv.coin_name]["total_value_usd"] += inv.amount * inv.purchase_price_usd
        coins_summary[inv.coin_name]["count"] += 1
    
    return {
        "database": "Replica (172.20.0.11)",
        "total_investments": len(investments),
        "total_value_usd": round(total_value, 2),
        "coins": coins_summary
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================
# STARTUP MESSAGE
# ============================================
@app.on_event("startup")
async def startup_event():
    print("=" * 60)
    print("🚀 Crypto Investment Tracker API Started")
    print("=" * 60)
    print("📊 Master DB (WRITE):  172.20.0.10:5432")
    print("📖 Replica DB (READ):  172.20.0.11:5432")
    print("🌐 API Documentation:  http://localhost:8000/docs")
    print("=" * 60)

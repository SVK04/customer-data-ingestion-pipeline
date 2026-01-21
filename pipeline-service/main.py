from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import engine, get_db, Base
import models.customer as models
from services.ingestion import ingest_customers
from logger import get_logger

logger = get_logger("pipeline-service")

try:
    logger.info("Initializing database tables...")
    models.Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized successfully")
except Exception as e:
    logger.critical(f"Failed to initialize database: {e}")
    raise

app = FastAPI()

@app.post("/api/ingest")
def start_ingestion(db: Session = Depends(get_db)):
    """Trigger the customer data ingestion process."""
    logger.info("Ingestion process triggered via POST /api/ingest")
    try:
        count = ingest_customers(db)
        logger.info(f"Ingestion completed successfully. Processed {count} records.")
        return {"status": "success", "records_processed": count}
    except Exception as e:
        logger.error(f"Ingestion process failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/customers")
def get_customers(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    db: Session = Depends(get_db)
):
    """Retrieve paginated list of customers from the database."""
    logger.debug(f"Fetching customers from DB: page={page}, limit={limit}")
    offset = (page - 1) * limit
    customers = db.query(models.Customer).offset(offset).limit(limit).all()
    total = db.query(models.Customer).count()
    
    logger.info(f"Retrieved {len(customers)} customers from DB (Total: {total})")
    return {
        "data": customers,
        "total": total,
        "page": page,
        "limit": limit
    }

@app.get("/api/customers/{customer_id}")
def get_customer(customer_id: str, db: Session = Depends(get_db)):
    """Retrieve a single customer by ID."""
    logger.debug(f"Fetching customer from DB by ID: {customer_id}")
    customer = db.query(models.Customer).filter(models.Customer.customer_id == customer_id).first()
    if not customer:
        logger.warning(f"Customer {customer_id} not found in DB")
        raise HTTPException(status_code=404, detail="Customer not found")
    
    logger.info(f"Found customer {customer_id} in DB")
    return customer

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

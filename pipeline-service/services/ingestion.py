from logger import get_logger
import requests
from models.customer import Customer

logger = get_logger("pipeline-service.ingestion")

from sqlalchemy.orm import Session

def ingest_customers(db_session: Session):
    """
    Fetches customer data from the mock server and syncs it with the local database.
    """
    import os
    # Using Docker service name 'mock' for internal networking
    mock_url = os.getenv("MOCK_SERVER_URL", "http://mock:5000")
    base_url = f"{mock_url}/api/customers"
    page = 1
    limit = 10
    total_processed = 0

    logger.info("Starting ingestion from mock server...")
    
    while True:
        params = {"page": page, "limit": limit}
        logger.debug(f"Fetching page {page} with limit {limit} from {base_url}")
        
        try:
            response = requests.get(base_url, params=params, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch data from mock server: {e}")
            db_session.rollback()
            raise

        result = response.json()
        customers_data = result.get("data", [])

        # Stop when empty list returned, signaling end of paginated source
        if not customers_data:
            logger.info("No more data received from mock server. Finishing ingestion.")
            break
        
        logger.info(f"Processing {len(customers_data)} records from page {page}")

        for item in customers_data:
            customer_id = item.get("customer_id")
            
            try:
                existing_customer = db_session.query(Customer).filter(Customer.customer_id == customer_id).first()

                if existing_customer:
                    logger.debug(f"Updating existing customer: {customer_id}")
                    for key, value in item.items():
                        # Safe update: only non-null fields from source overwrite existing data
                        if value is not None and hasattr(existing_customer, key):
                            setattr(existing_customer, key, value)
                else:
                    logger.debug(f"Inserting new customer: {customer_id}")
                    new_customer = Customer(
                        customer_id=item.get("customer_id"),
                        first_name=item.get("first_name"),
                        last_name=item.get("last_name"),
                        email=item.get("email"),
                        phone=item.get("phone"),
                        address=item.get("address"),
                        date_of_birth=item.get("date_of_birth"),
                        account_balance=item.get("account_balance"),
                        created_at=item.get("created_at")
                    )
                    db_session.add(new_customer)
                
                total_processed += 1
            except Exception as e:
                logger.error(f"Error processing customer record {customer_id}: {e}")
                continue

        page += 1

    logger.info(f"Committing {total_processed} updates/inserts to database...")
    try:
        # Single atomic commit for the entire batch to ensure data consistency
        db_session.commit()
        logger.info("Database commit successful.")
    except Exception as e:
        logger.critical(f"Failed to commit changes to database: {e}")
        db_session.rollback()
        raise

    return total_processed

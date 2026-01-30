from app.core.config import settings
from app.core.logger import logger
from app.core.schema import SubAccountCreateSchema, TransactionInitializeSchema
import httpx
class PaystackService:
    def __init__(self, secret_key: str = settings.PAYSTACK_SECRET_KEY):
        self.secret_key = secret_key
        self.headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json"
        }
        self.BASE_URL = "https://api.paystack.co"

    async def list_banks(self):
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.get(
                f"{self.BASE_URL}/bank", 
                headers=self.headers
            )
            return response.json()
        
    async def verify_account(self, account_number: str, bank_code: str):
        params = {
            "account_number": account_number,
            "bank_code": bank_code
        }

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.get(
                f"{self.BASE_URL}/bank/resolve", 
                headers=self.headers,
                params=params,      
            )
            try:
                response_json = response.json()
            except Exception:
                response_json = response.text

            if response.status_code >= 400:
                logger.error(f"Paystack account verification failed: Status {
                             response.status_code}, Response: {response_json}")

            return response_json
        
    async def verify_transaction(self, reference: str):
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.get(
                f"{self.BASE_URL}/transaction/verify/{reference}", 
                headers=self.headers
            )
            return response.json()

    async def list_transactions(self, per_page: int = 50, page: int = 1):
        params = {"perPage": per_page, "page": page}
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.get(
                f"{self.BASE_URL}/transaction", 
                headers=self.headers, 
                params=params
            )
            return response.json()
        
    async def create_subaccount(self, data: SubAccountCreateSchema):
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{self.BASE_URL}/subaccount", 
                json=data.model_dump(), 
                headers=self.headers
            )
            try:
                response_json = response.json()
            except Exception:
                response_json = response.text

            if response.status_code >= 400:
                logger.error(f"Paystack subaccount creation failed: Status {
                             response.status_code}, Response: {response_json}")
            else:
                logger.info(f"Paystack subaccount creation successful: Status {
                            response.status_code}")
            return response_json
        
    async def initialize_transaction(self, data: TransactionInitializeSchema):       
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{self.BASE_URL}/transaction/initialize", 
                headers=self.headers,
                json=data.model_dump(exclude_none=True)
            )

            try:
                response_json = response.json()
            except Exception:
                response_json = response.text

            if response.status_code >= 400:
                logger.error(f"Paystack initialization failed: Status {
                            response.status_code}, Response: {response_json}")
            else:
                logger.info(f"Paystack initialization successful: Status {
                            response.status_code}")

            return response_json
        
paystack_service = PaystackService()
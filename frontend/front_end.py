from api_client import APIClient
from app import RAGilityApp

api_client = APIClient(base_url="http://localhost:8000")
app = RAGilityApp(api_client)
app.run()

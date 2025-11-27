import requests
from typing import Optional, Dict


class APIClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    def _get_headers(self, token: Optional[str] = None) -> Dict[str, str]:
        if token:
            return {"Authorization": f"Bearer {token}"}
        return {}
    
    def register(self, name: str, password: str, email: str) -> requests.Response:
        url = f"{self.base_url}/register"
        payload = {"name": name, "password": password, "email": email}
        return requests.post(url, json=payload)
    
    def login(self, name: str, password: str) -> requests.Response:
        url = f"{self.base_url}/login"
        payload = {"name": name, "password": password}
        return requests.post(url, json=payload)
    
    def get_profile(self, token: str) -> requests.Response:
        url = f"{self.base_url}/profile/"
        headers = self._get_headers(token)
        return requests.get(url, headers=headers)
    
    def get_collections(self, token: str) -> requests.Response:
        url = f"{self.base_url}/collections/"
        headers = self._get_headers(token)
        return requests.get(url, headers=headers)
    
    def create_collection(self, name: str, token: str) -> requests.Response:
        url = f"{self.base_url}/collections"
        payload = {"name": name}
        headers = self._get_headers(token)
        return requests.post(url, json=payload, headers=headers)
    
    def upload_document(self, file_name: str, file_content: bytes, 
                       collection_id: int, token: str) -> requests.Response:
        url = f"{self.base_url}/documents/upload"
        files = {"file": (file_name, file_content)}
        params = {"collection_id": collection_id}
        headers = self._get_headers(token)
        return requests.post(url, files=files, params=params, headers=headers)
    
    def get_chat_history(self, collection_id: int, token: str) -> requests.Response:
        url = f"{self.base_url}/chat-history/{collection_id}"
        headers = self._get_headers(token)
        return requests.get(url, headers=headers)
    
    def query_simple(self, collection_id: int, query: str, token: str) -> requests.Response:
        url = f"{self.base_url}/query/simple"
        payload = {"collection_id": collection_id, "query": query}
        headers = self._get_headers(token)
        return requests.post(url, json=payload, headers=headers)
    
    def query_chat(self, collection_id: int, query: str, token: str) -> requests.Response:
        url = f"{self.base_url}/query/chat"
        payload = {"collection_id": collection_id, "query": query}
        headers = self._get_headers(token)
        return requests.post(url, json=payload, headers=headers)

import requests

def fetch_mock_data():
    url = "http://127.0.0.1:8000/mock_data"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

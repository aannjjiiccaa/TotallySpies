import requests


def fetch_data():
    url = "http://127.0.0.1:8000/data"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def process_data(data):
    """
    Very small placeholder for repo-level processing logic.
    """
    if "error" in data:
        return data

    # Example: ensure data is iterable and count items
    if isinstance(data, list):
        return {"item_count": len(data)}
    return {"received": data}


if __name__ == "__main__":
    raw_data = fetch_data()
    result = process_data(raw_data)
    print(result)

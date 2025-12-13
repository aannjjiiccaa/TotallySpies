from services.call_api import fetch_mock_data
from funcs.add import Adder
from funcs.mul import Multiplier
from funcs.div import divide

def main():
    print("Fetching data from Project B...")
    data = fetch_mock_data()
    print("Received:", data)
    adder = Adder(5,1)
    muler = Multiplier(5,6)
    result = divide(muler.add(),adder.add())
    print(result)

if __name__ == "__main__":
    main()

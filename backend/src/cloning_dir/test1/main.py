from services.call_api import fetch_data
from funcs.add import Adder
from funcs.mul import Multiplier
from funcs.div import divide
from neutal_network.cifar_10_nn import my_model
from estimators.maximum_likelihood_estimator import prvi_izvod, drugi_izvod

def main():
    print("Fetching data from Project Neural Network and Estimators...")
    data = fetch_data()
    print("Received:", data)
    adder = Adder(5,1)
    muler = Multiplier(5,6)
    neural_network = my_model()
    print(prvi_izvod(adder))


if __name__ == "__main__":
    main()

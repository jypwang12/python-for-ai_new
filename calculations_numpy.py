# This is an Object Oriented Programming (OOP) example in Python.
# This code defines a Calculation class and uses the numpy library to calculate the mean and median of a list of numbers.

import numpy as np


class Calculation:
    def __init__(self, data):
        # self.data is an instance variable
        # that holds the data passed to the class.
        self.data = data

    # calculate_mean and calculate_median are methods of the Calculation class,
    # they are functions that operate on the data and return the mean and median, respectively.
    def calculate_mean(self):
        return np.mean(self.data)

    def calculate_median(self):
        return np.median(self.data)


if __name__ == "__main__":
    data = [80, 82, 85, 90, 95]
    # calc is an instance of the Calculation class, it is a variable.
    calc = Calculation(data)
    # calculate_mean and calculate_median are methods of the Calculation class,
    # they are functions that operate on the data and return the mean and median, respectively.
    print("Mean:", calc.calculate_mean())
    print("Median:", calc.calculate_median())

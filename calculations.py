# Python script example for calculating mean and median of a list of numbers.

# Sample data, it is a list of numbers
# It is a constant for the purpose of this script,
# it is not meant to be changed.

data = [80, 82, 85, 90, 95]

# Calculate the mean of the data
# It is a variable, it is a floating point number.
# Python variables are dynamically typed,
# so we don't need to declare the type of the variable before using it.

sum = 0

# calculate the sum using a for loop
for i in range(len(data)):
    sum += data[i]
    print(f"Adding {data[i]}, current sum: {sum}")
mean = sum / len(data)

print("Data Mean:", mean)

# Calculate the median of the data
# We use a if logical statement to check
# if the number of elements in the data is even or odd,
sorted_data = sorted(data)
n = len(sorted_data)
if n % 2 == 0:
    print("Data has even number of elements.")
    median = (sorted_data[n // 2 - 1] + sorted_data[n // 2]) / 2
else:
    print("Data has odd number of elements.")
    median = sorted_data[n // 2]
print("Data Median:", median)

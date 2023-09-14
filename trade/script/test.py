def round_to_nearest_50(input_value):
    # Calculate the rounded value
    rounded_value = round(input_value / 50) * 50
    return rounded_value

# Test cases
test_cases = [20105, 20145, 20162, 20188]

for value in test_cases:
    output = round_to_nearest_50(value)
    print(f"Value: {value}, Output: {output}")

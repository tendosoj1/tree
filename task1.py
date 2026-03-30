#test
# Function to read the city data from a file
def read_city_file(filename):

    # Create an empty dictionary to store the city information
    # The structure will be:
    # { "City": [(Destination, actual_distance, straight_distance), ...] }
    city_dict = {}

    # Open the file in read mode ("r")
    # The 'with' statement automatically closes the file after reading
    with open(filename, "r") as file:

        # Loop through each line in the file
        for line in file:

            # Remove spaces and newline characters from the start and end of the line
            line = line.strip()

            # If the line is empty, skip it and continue to the next line
            if not line:
                continue

            # Split the line into parts using spaces as the separator
            # Example line:
            # "Melbourne Sydney 878 713"
            # becomes:
            # ["Melbourne", "Sydney", "878", "713"]
            parts = line.split()

            # Extract the starting city (first column)
            from_city = parts[0]

            # Extract the destination city (second column)
            to_city = parts[1]

            # Convert the actual distance from string to integer
            actual_distance = int(parts[2])

            # Convert the straight-line distance from string to integer
            straight_line_distance = int(parts[3])

            # Check if the starting city is already a key in the dictionary
            if from_city not in city_dict:

                # If not, create a new entry with an empty list
                # This list will store all destinations from this city
                city_dict[from_city] = []

            # Add the destination information as a tuple
            # The tuple contains:
            # (destination city, actual distance, straight-line distance)
            city_dict[from_city].append(
                (to_city, actual_distance, straight_line_distance)
            )

    # After reading all lines, return the completed dictionary
    return city_dict


# ----------- MAIN PROGRAM -----------

# Name of the input file containing city information
filename = "cities.txt"

# Call the function to read and process the file
data = read_city_file(filename)

# Print the resulting dictionary to show the stored data
print(data)

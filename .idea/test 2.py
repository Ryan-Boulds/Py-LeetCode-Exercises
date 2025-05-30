import requests
from bs4 import BeautifulSoup

def print_secret_message(doc_url):
    # Get the Google Doc's content
    response = requests.get(doc_url)
    # Throws an exception for if an error occurs in obtaining the document.
    response.raise_for_status()

    # Get the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the rows in the document. We don't need any other text in the document.
    rows = soup.find_all('tr')[1:]

    # Store the coords and x-y coords here
    grid_data = []
    # Loop through each row to add each element to the grid_data list.
    for row in rows:
        cols = row.find_all('td')

        # Makes sure that there are 3 columns in each row.
        # This prevents things that we only get the data that we want.
        if len(cols) == 3:
            x = int(cols[0].text.strip())  # First column: x-coord
            char = cols[1].text.strip()    # Second column: char
            y = int(cols[2].text.strip())  # Third column: y-coord
            # Adds the character and the location to be drawn to the list.
            grid_data.append((char, x, y))

    # Find the size of the grid
    max_x = max(x for _, x, _ in grid_data) if grid_data else 0
    max_y = max(y for _, _, y in grid_data) if grid_data else 0

    # Draw a grid of blank spaces for the size needed. (After, we will substitute those spaces for the charcters)
    grid = [[' ' for _ in range(max_x + 1)] for _ in range(max_y + 1)]

    # Place characters in the grid where there x-y coords are.
    for char, x, y in grid_data:
        grid[y][x] = char

    # Because the way that the terminal prints is upsidedown compared to a traditional graph,
    # We must flip the graph upsidedown when we print it.
    for row in reversed(grid):
        print(''.join(row))

# Test with the provided URL
if __name__ == "__main__":
    url = 'https://docs.google.com/document/d/e/2PACX-1vQGUck9HIFCyezsrBSnmENk5ieJuYwpt7YHYEzeNJkIb9OSDdx-ov2nRNReKQyey-cwJOoEKUhLmN9z/pub'
    print_secret_message(url)
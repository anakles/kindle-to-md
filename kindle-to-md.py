import argparse
import requests
import getpass
import subprocess
from bs4 import BeautifulSoup


# Define the target URL
URL = "https://read.amazon.com/notebook"


# Fetch the library list from site
def fetch_books(cookie: str):
    
    # Prepare headers with the provided cookie
    headers = {
        "Cookie": cookie
    }
    
    try:
        # Send the GET request
        response = requests.get(URL, headers=headers)
        response.raise_for_status()  # Raise an error for bad responses (4xx and 5xx)
        return response.text

    except requests.RequestException as e:
        print(f"Error fetching data: {e}")


# Parses the HTML code of the site to identify the books available
def parse_library_div(response_body: str):
    """Parses the HTML response body and extracts all elements inside the target div."""
    soup = BeautifulSoup(response_body, "html.parser")
    
    # Find the target div
    target_div = soup.find("div", {"id": "kp-notebook-library", "class": "a-row"})
    
    if target_div:
        # Extract all elements inside the div
        elements = [str(element) for element in target_div.contents if element != "\n"]
        return elements
    else:
        print("Target div not found.")
        return []


# Write the transformed notes to the specified output file
def write_to_file(output_path, file_content):
    # Save response content to the output file
    with open(output_path, "w", encoding="utf-8") as file:
        file.write(file_content)
        
    print(f"Data successfully saved to {output_path}")


# Parses the identified HTML elements corresponding to books into python objects
def parse_books(book_elements):
    """Parses book elements into structured book objects."""
    books = []
    for book_html in book_elements:
        book_soup = BeautifulSoup(book_html, "html.parser")
        
        book_div = book_soup.find("div", class_="kp-notebook-library-each-book")
        if not book_div:
            print("Warning: Skipping a book entry due to missing 'kp-notebook-library-each-book' div.")
            continue  # Skip this book entry
        
        asin = book_div.get("id", "Unknown ASIN")
        title_tag = book_soup.find("h2")
        author_tag = book_soup.find("p")
        date_input = book_soup.find("input", {"id": f"kp-notebook-annotated-date-{asin}"})
        
        title = title_tag.text.strip() if title_tag else "Unknown Title"
        author = author_tag.text.replace("By: ", "").strip() if author_tag else "Unknown Author"
        date = date_input.get("value", "Unknown Date") if date_input else "Unknown Date"
        
        books.append({"ASIN": asin, "Title": title, "Author": author, "Date": date})
    
    return books


# Prompts the user to select a book using fzf
def select_book(books):

    if not books:
        print("No books available for selection.")
        return None

    # Format books for display
    book_list = [f"{book['Title']} - {book['Author']} ({book['Date']})" for book in books]

    # Run fzf
    fzf_result = subprocess.run(
        ["fzf"], input="\n".join(book_list), text=True, capture_output=True
    )

    selected_title = fzf_result.stdout.strip()
    if not selected_title:
        print("No book selected.")
        return None

    # Find selected book
    for book in books:
        if selected_title.startswith(book["Title"]):
            return book

    print("Selected book not found in the list.")
    return None


# Fetches the notebook page for the given ASIN and returns the response body
def fetch_annotations(asin, cookie):
    url = f"{URL}?asin={asin}&contentLimitState="

    headers = {
        "Cookie": cookie
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an error for bad responses (4xx and 5xx)
        return response.text  # Return the response body (HTML)
    except requests.RequestException as e:
        print(f"Error fetching notebook page: {e}")
        return None


# Parses the identified HTML elements corresponding to notes into python objects
def parse_highlights(highlight_html):
    hl_list = []

    soup = BeautifulSoup(highlight_html, "html.parser")
    
    # Extract all divs with the class 'kp-notebook-highlight' (this identifies highlighted text)
    highlights = soup.find_all('div', class_='kp-notebook-row-separator')

    if not highlights:
        print("Warning: No highlights found for this book")
        return []

    for hl in highlights:
        hl = str(hl)
        if hl is None:
            print("Encountered None, skipping...")
            continue  # Skip the iteration if `hl` is None
        
        hl_soup = BeautifulSoup(hl, "html.parser")

        try:
            text_tag = hl_soup.find('div', class_='kp-notebook-highlight')
            if text_tag:
                text = text_tag.get_text(strip=True)
            position_tag = hl_soup.find('input', {'id': 'kp-annotation-location'})
            if position_tag:
                position = position_tag.get('value')
            notes_tag = hl_soup.find('span', {'id': 'note'})
            if notes_tag:
                note = notes_tag.get_text(strip=True)

            if position is not None and text is not None:
                hl_list.append({"Highlight": text, "Position": position, "Note": note})
            else:
                print("Either position or text is None. Skipping this entry.")

        except Exception as e:
            # Catch any errors that might occur
            print(f"An error occurred: {e}")

    if not hl_list:
        print("Warning: This book has no notes or highlights")
        return []

    return hl_list


# Transform highlights to markdown strings
def highlights_to_md(highlights):
    markdown_quotes = []
    
    # Iterate over each highlight in the list
    for highlight in highlights:
        # Format each highlight as Markdown
        markdown_string = f"> [!quote] Position {highlight['Position']}:\n> {highlight['Highlight']}"
        markdown_quotes.append(markdown_string)
    
    return markdown_quotes


# run
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch data from a predefined URL using a provided cookie.")
    parser.add_argument("output_path", type=str, help="Path to save the output file")
    
    args = parser.parse_args()
    
    # Prompt the user for the cookie without displaying input
    cookie = getpass.getpass("Enter the cookie: ")
    output_path = args.output_path

    html_books = fetch_books(cookie)
    if html_books:
        books = parse_library_div(html_books)
        books = parse_books(books)

    selected_book = select_book(books)
    if selected_book:
        print("You selected:", selected_book)

    # Get annotations for book specified by ASIN
    html_notes = fetch_annotations(selected_book["ASIN"], cookie)
    if html_notes:
        print("Annotations fetched successfully!")
        parsed_highlights = parse_highlights(html_notes)
      
        if parsed_highlights:
            markdown = highlights_to_md(parsed_highlights)
            full_markdown = "\n\n".join(markdown)

            write_to_file(output_path + selected_book["Title"], full_markdown)


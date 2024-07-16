import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import csv

url = "https://farside.co.uk/?p=1321"

def fetch_page(url, retries=3):
    for i in range(retries):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"Attempt {i+1} failed: {e}")
            time.sleep(2)
    return None

def convert_date(date_str):

    try:
        date_obj = datetime.strptime(date_str, '%d %b %Y')
        return date_obj.strftime('%Y-%m-%d')
    except ValueError as e:
        print(f"Error converting date: {e}")
        return date_str


def parse_cell(cell_text):
    cell_text = cell_text.replace(',', '')

    try:
        return float(cell_text)
    except ValueError:
        if cell_text == "-":
            return 0.0
        
        elif cell_text.startswith("(") and cell_text.endswith(")"):
            return -float(cell_text[1:-1])
        
        else:
            raise ValueError(f"Unexpected format in table cell: {cell_text}")
        
def write_to_csv(headers, rows, file_path='farside.csv'):
    with open(file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(rows)

def main():
    response = fetch_page(url)

    if response:

        soup = BeautifulSoup(response.content, 'html.parser')

        etf_table = soup.find('table', class_='etf')

        if etf_table:
            headers = [header.text.strip() for header in etf_table.find_all('th')]
            rows = []

            for row in etf_table.find_all('tr')[2:-4]:
                cells = row.find_all('td')

                row_data = [convert_date(cells[0].text)] +  [parse_cell(cell.text) for cell in cells[1:]]
                rows.append(row_data)

            write_to_csv(headers, rows)
        
    else:
        print("Failed to retrieve the page after multiple attempts.")

main()
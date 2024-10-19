import requests
import mwparserfromhell
import time

# API endpoint
API_ENDPOINT = "https://liquipedia.net/valorant/api.php"

# Custom headers to comply with Liquipedia's guidelines
headers = {
    'User-Agent': 'ValorantHackathonDataScraper/1.0 (chdinghao@gmail.com)',
    'Accept-Encoding': 'gzip'
}

# Cache to store API responses
cache = {}

# Function to make a safe API request with rate limiting
def make_api_request(params):
    try:
        response = requests.get(API_ENDPOINT, params=params, headers=headers)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

    # Wait for 2 seconds to comply with rate limiting
    time.sleep(2)
    return data

# Step 1: Get the list of pages in a category
def get_category_members(category_title):
    params = {
        'action': 'query',
        'list': 'categorymembers',
        'cmtitle': f'Category:{category_title}',
        'format': 'json',
        'cmlimit': 'max'
    }
    data = make_api_request(params)
    if data:
        pages = data.get('query', {}).get('categorymembers', [])
        return pages
    else:
        return []

# Step 2: Retrieve and parse each page
def get_page_content(page_id):
    if page_id in cache:
        return cache[page_id]
    else:
        params = {
            'action': 'query',
            'prop': 'revisions',
            'rvprop': 'content',
            'pageids': page_id,
            'format': 'json'
        }
        data = make_api_request(params)
        if data:
            cache[page_id] = data
        return data

# Main function
def main():
    # Specify the category you want to scrape
    category_title = 'Tournaments'

    # Open a file to write the output
    with open('templates_output.txt', 'w', encoding='utf-8') as outfile:
        # Get pages in the category
        pages = get_category_members(category_title)

        # Process each page
        for page in pages:
            page_id = page['pageid']
            title = page['title']

            # Get page content
            page_data = get_page_content(page_id)
            if not page_data:
                print(f"Failed to retrieve data for page: {title}")
                continue

            page_info = page_data.get('query', {}).get('pages', {}).get(str(page_id), {})
            revisions = page_info.get('revisions', [])

            if not revisions:
                print(f"No revisions found for page: {title}")
                continue

            wikitext = revisions[0].get('*', '')

            # Parse wikitext using mwparserfromhell
            wikicode = mwparserfromhell.parse(wikitext)

            # Write to the output file
            outfile.write(f"\nPage: {title}\n")
            for template in wikicode.filter_templates():
                template_name = template.name.strip()
                outfile.write(f"Template: {template_name}\n")
                for param in template.params:
                    param_name = param.name.strip()
                    param_value = param.value.strip()
                    outfile.write(f"  {param_name} = {param_value}\n")

    # Attribution notice
    print("\nData has been written to 'templates_output.txt'.")
    print("Data sourced from Liquipedia.net under CC-BY-SA 3.0 License.")

if __name__ == "__main__":
    main()
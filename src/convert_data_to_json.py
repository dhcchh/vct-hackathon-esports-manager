import json

def parse_text_file(input_file):
    pages = []
    current_page = None
    current_template = None

    with open(input_file, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.rstrip('\n')

            # Check for a new page
            if line.startswith('Page: '):
                # Save the previous page if it exists
                if current_page is not None:
                    pages.append(current_page)

                # Start a new page
                page_title = line[len('Page: '):].strip()
                current_page = {
                    'Page': page_title,
                    'Templates': []
                }
                current_template = None

            # Check for a new template
            elif line.startswith('Template: '):
                # Start a new template
                template_name = line[len('Template: '):].strip()
                current_template = {
                    'Template': template_name,
                    'Parameters': {}
                }
                if current_page is not None:
                    current_page['Templates'].append(current_template)
                else:
                    print(f"Warning: Template '{template_name}' found outside of a page.")
                    continue  # Skip templates outside of pages

            # Check for a parameter (lines starting with two spaces)
            elif line.startswith('  ') and current_template is not None:
                # Extract parameter name and value
                param_line = line.strip()
                if ' = ' in param_line:
                    param_name, param_value = param_line.split(' = ', 1)
                    current_template['Parameters'][param_name.strip()] = param_value.strip()
                else:
                    print(f"Warning: Malformed parameter line '{line}'.")

            # Ignore empty lines or other content
            else:
                continue

        # Add the last page to the list if it exists
        if current_page is not None:
            pages.append(current_page)

    return pages

def save_to_json(data, output_file):
    with open(output_file, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

def main():
    input_file = 'input.txt'   # Replace with your input file name
    output_file = 'output.json'  # The output JSON file

    # Parse the text file
    data = parse_text_file(input_file)

    # Save the data to a JSON file
    save_to_json(data, output_file)

    print(f"Data has been successfully converted to JSON and saved to '{output_file}'.")

if __name__ == '__main__':
    main()
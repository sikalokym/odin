from lxml import etree

# @author Hassan Wahba

def parse_xml(xml_data, template):
    """
    Parse the given XML data using the provided template.

    Args:
        xml_data (str): The XML data to be parsed.
        template (str): The template used to extract data from the XML.

    Returns:
        dict: A dictionary containing the extracted data.

    """
    # Parse the XML
    root = etree.fromstring(xml_data)

    # Using the template to extract data
    data = extract_data(template, root)
    return data

def extract_data(template, element):
    """
    Extracts data from an XML element based on a given template.

    Args:
        template (dict): A dictionary representing the template for extracting data.
            The keys represent the names of the extracted data fields, and the values
            represent the paths to locate the data within the XML element.
        element (Element): The XML element from which to extract the data.

    Returns:
        dict: A dictionary containing the extracted data. The keys correspond to the
            names of the data fields, and the values contain the extracted data.

    """
    if template == {}:
        return element.text
    extracted_data = {}
    for key, path in template.items():
        if isinstance(path, dict):
            if key == 'PackageDataRows':
                extracted_data[key] = [extract_alternating_data(path['children'], child) for child in element.findall(path['path'])]
            else:
                extracted_data[key] = [extract_data(path['children'], child) for child in element.findall(path['path'])]
        else:
            extracted_data[key] = element.findtext(path)
    return extracted_data

def extract_alternating_data(template, item_element):
    """
    Extracts alternating `VariantRules` and `Content` from an XML element, 
    grouping them into pairs.

    Args:
        template (dict): The template for extracting `VariantRules` and `Content`.
        item_element (Element): The XML element representing the `Item`, which contains 
                                alternating `VariantRules` and `Content` elements.

    Returns:
        list: A list of dictionaries, each representing a paired `VariantRules` and `Content`.
    """
    items = []
    current_variant = None
    # Iterate over each child in the item element
    for child in item_element:
        if child.tag == 'VariantRules' or child.tag == 'Content':
            # Use the template to extract data for VariantRules or Content
            extracted = extract_data({child.tag: template[child.tag]}, child)
            if child.tag == 'VariantRules':
                # Start a new pair with the current VariantRule
                current_variant = {'VariantRules': extracted, 'Content': []}
            elif child.tag == 'Content' and current_variant is not None:
                # Add the Content to the current VariantRule's list of Contents
                current_variant['Content'].append(extracted)
                # Assuming Content always follows VariantRules, add the pair to items
                items.append(current_variant)
                current_variant = None  # Reset for the next VariantRules, if any
        elif child.tag == 'Code':
            items.append({child.tag: child.text})
        elif child.tag == 'Text':
            items.append({'Title': child.text})

    return items

from lxml import etree

from main import extract
from parser import extract_path_value
from pipelines.scanners.base import get_mappings
from io import StringIO, BytesIO


def get_config_file_name():
    return 'pom.xml',

def update_content(content, projects:set, project_mappings):
    mappings = get_mappings()
    updated_keys = set()
    elements = etree.fromstring(content.encode())
    first_line = ""
    if 'encoding' in content.split('\n')[0]:
        first_line = content.split('\n')[0] + '\n'
    for element in elements:
        if element.tag.endswith('properties'):
            print(element)
            for prop in element:
                if prop.tag in mappings.keys():
                    updated_keys.add(prop.tag)
                    for project in projects:
                        if project in project_mappings:
                            prop.text = extract_path_value(obj=project_mappings[project], path=mappings[prop.tag], default='')
            for key, path in mappings.items():
                if key not in updated_keys:
                    new_element = etree.Element('{' + element.nsmap[None] + '}' + key)
                    for project in projects:
                        if project in project_mappings:
                            new_element.text = extract_path_value(obj=project_mappings[project], path=path, default='')
                            new_element.tail = '\n '
                    element.append(new_element)
            break
    etree.indent(elements)
    return dict(updated_content=first_line+etree.tostring(elements,pretty_print=True).decode(), is_updated=True)


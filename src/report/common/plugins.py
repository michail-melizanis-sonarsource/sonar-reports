from collections import defaultdict

from parser import extract_path_value
from report.utils import generate_section
from utils import multi_extract_object_reader


def process_plugins(directory, extract_mapping, server_id_mapping):
    plugins = defaultdict(list)
    for url, plugin in multi_extract_object_reader(directory=directory, mapping=extract_mapping, key='getPlugins'):
        server_id = server_id_mapping[url]
        plugin_type = extract_path_value(obj=plugin, path='$.type')
        if plugin_type == 'EXTERNAL':
            plugins[server_id].append(
                dict(
                    server_id=server_id,
                    name=extract_path_value(obj=plugin, path='$.name'),
                    description=extract_path_value(obj=plugin, path='$.description'),
                    version=extract_path_value(obj=plugin, path='$.version'),
                    homepage_url=extract_path_value(obj=plugin, path='$.homepageUrl')
                )
            )
    return plugins


def generate_plugin_markdown(directory, extract_mapping, server_id_mapping):
    plugins = process_plugins(directory=directory, extract_mapping=extract_mapping, server_id_mapping=server_id_mapping)
    return generate_section(
        headers_mapping={"Server ID": "server_id", "Plugin Name": "name", "Description": "description",
                         "Version": "version", "Home Page URL": "homepage_url"},
        title='Installed Plugins', level=2,
        rows=[plugin for server_plugins in plugins.values() for plugin in server_plugins]
    ), plugins

from collections import defaultdict

from utils import multi_extract_object_reader

TEMPLATE = """
## Installed Plugins
| Server ID | Plugin Name | Description | Version | Home Page URL |
|:----------|:------------|:------------|:--------|:--------------|
{plugins}
"""


def process_plugins(directory, extract_mapping, server_id_mapping):
    plugins = defaultdict(list)
    for url, plugin in multi_extract_object_reader(directory=directory, mapping=extract_mapping, key='getPlugins'):
        server_id = server_id_mapping[url]
        if "sonar" not in plugin.get('organizationName', 'sonar').lower() and plugin['type'] != 'BUNDLED':
            plugins[server_id].append(
                dict(
                    server_id=server_id,
                    name=plugin['name'],
                    description=plugin['description'],
                    version=plugin['version'],
                    homepageUrl=plugin['homepageUrl']
                )
            )
    return plugins

def format_plugins(plugins):
    return "\n".join([
        "| {server_id} | {name} | {description} | {version} | {homepageUrl} |".format(
            server_id=plugin['server_id'],
            name=plugin['name'],
            description=plugin['description'],
            version=plugin['version'],
            homepageUrl=plugin['homepageUrl']
        ) for server_plugins in plugins.values() for plugin in server_plugins
    ])

def generate_plugin_markdown(directory, extract_mapping, server_id_mapping):
    plugins = process_plugins(directory=directory, extract_mapping=extract_mapping, server_id_mapping=server_id_mapping)
    return TEMPLATE.format(plugins=format_plugins(plugins=plugins)), plugins

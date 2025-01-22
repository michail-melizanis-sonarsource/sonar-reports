from collections import defaultdict
from constants import BUILTIN_REPOS
from report.utils import generate_section

from utils import multi_extract_object_reader


def process_rules(directory, extract_mapping, server_id_mapping, plugins):
    template_rules = defaultdict(set)
    plugin_rules = defaultdict(set)
    for url, rule in multi_extract_object_reader(directory=directory, mapping=extract_mapping, key='getRules'):
        server_id = server_id_mapping[url]
        if rule.get('templateKey'):
            template_rules[server_id].add(rule['key'])
        if rule['repo'] not in BUILTIN_REPOS and len(plugins[server_id]) > 0:
            plugin_rules[server_id].add(rule['key'])
    return template_rules, plugin_rules


def process_profile_rules(directory, extract_mapping, server_id_mapping):
    profiles = defaultdict(dict)
    for url, rule_dict in multi_extract_object_reader(directory=directory, mapping=extract_mapping,
                                                      key='getProfileRules'):
        server_id = server_id_mapping[url]
        for rule_key, actives in rule_dict.items():
            if not isinstance(actives, list):
                continue
            for profile in actives:
                if profile['qProfile'] not in profiles[server_id].keys():
                    profiles[server_id][profile['qProfile']] = set()
                profiles[server_id][profile['qProfile']].add(rule_key)
    return profiles


def process_profile_projects(server_projects, profile_rules, template_rules, plugin_rules):
    profile_projects = defaultdict(dict)
    for server_id, projects in server_projects.items():
        for project in projects:
            for profile in project['profiles']:
                if profile not in profile_projects[server_id].keys():
                    profile_projects[server_id][profile] = set()
                profile_projects[server_id][profile].add(project['key'])
                rules = profile_rules[server_id].get(profile, set())
                project['rules'] += len(rules)
                project['template_rules'] += len(template_rules[server_id].intersection(rules))
                project['plugin_rules'] += len(plugin_rules[server_id].intersection(rules))
    return profile_projects


def process_quality_profiles(directory, extract_mapping, server_id_mapping, profile_projects, profile_rules,
                             template_rules, plugin_rules):
    profiles = list()
    for url, profile in multi_extract_object_reader(directory=directory, mapping=extract_mapping, key='getProfiles'):
        server_id = server_id_mapping[url]
        rules = profile_rules[server_id].get(profile['key'], set())
        profiles.append(dict(
            server_id=server_id,
            language=profile['language'],
            key=profile['key'],
            name=profile['name'],
            is_built_in=profile.get('isBuiltIn', False),
            is_default="Yes" if profile.get('isDefault', False) else "No",
            parent=profile.get('parentName', ""),
            rules=rules,
            rule_count=len(rules),
            template_rules=len(template_rules[server_id].intersection(rules)),
            plugin_rules=len(plugin_rules[server_id].intersection(rules)),
            projects=profile_projects[server_id].get(profile['key'], set()),
            project_count=len(profile_projects[server_id].get(profile['key'], set()))
        ))
    return profiles


def generate_profile_markdown(directory, extract_mapping, server_id_mapping, projects, plugins):
    template_rules, plugin_rules = process_rules(directory=directory, extract_mapping=extract_mapping,
                                                 server_id_mapping=server_id_mapping, plugins=plugins)
    profile_rules = process_profile_rules(directory=directory, extract_mapping=extract_mapping,
                                          server_id_mapping=server_id_mapping)
    profile_projects = process_profile_projects(server_projects=projects, profile_rules=profile_rules,
                                                template_rules=template_rules, plugin_rules=plugin_rules)
    profiles = process_quality_profiles(directory=directory, extract_mapping=extract_mapping,
                                        server_id_mapping=server_id_mapping, profile_projects=profile_projects,
                                        profile_rules=profile_rules, plugin_rules=plugin_rules,
                                        template_rules=template_rules)
    active_profiles = generate_section(
        headers_mapping={'Server ID': 'server_id', 'Language': 'language', 'Quality Profile Name': 'name',
                         'Parent Profile': 'parent', 'Default Profile': 'is_default', 'Total Rules': 'rule_count',
                         'Template Rules': 'template_rules', 'Rules from 3rd party plugins': 'plugin_rules',
                         '# of Projects using': 'project_count'},
        rows=profiles, title='Quality Profiles', level=2, sort_by_lambda=lambda x: x['project_count'],
        sort_order='desc',
        filter_lambda=lambda x: len(x['projects']) > 0 or x['is_default'] == "Yes" and not x['is_built_in']
    )
    inactive_profiles = generate_section(
        headers_mapping={'Server ID': 'server_id', 'Language': 'language', 'Quality Profile Name': 'name',
                         'Parent Profile': 'parent', 'Total Rules': 'rule_count', 'Template Rules': 'template_rules',
                         'Rules from 3rd party plugins': 'plugin_rules'},
        rows=profiles, title='Quality Profiles', level=2, sort_by_lambda=lambda x: x['project_count'],
        sort_order='asc',
        filter_lambda=lambda x: x['project_count'] == 0 and x['is_default'] == "No" and not x['is_built_in']
    )

    return active_profiles, inactive_profiles

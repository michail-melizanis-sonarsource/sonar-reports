from collections import defaultdict
import os
import json
from datetime import datetime

from parser import extract_path_value
from constants import BUILTIN_REPOS
from utils import object_reader

MARKDOWN_PATH = __file__.replace('generate.py', 'template.md')


def extract_multi_branch_projects(extract_directory):
    projects = dict()
    for branch in object_reader(directory=extract_directory, key='getBranches'):
        if not branch.get('excludedFromPurge'):
            continue
        if branch['projectKey'] not in projects.keys():
            projects[branch['projectKey']] = set()
        projects[branch['projectKey']].add(branch['name'])
    return {k for k, v in projects.items() if len(v) > 1}


def extract_pull_request_projects(extract_directory):
    projects = dict()
    for pull_request in object_reader(directory=extract_directory, key='getProjectPullRequests'):
        projects[pull_request['projectKey']] = extract_path_value(obj=pull_request, path='$.paging.total')
    return set(projects.keys())


def format_devops_bindings(extract_directory, devops_bindings: dict):
    multi_branch_projects = extract_multi_branch_projects(extract_directory=extract_directory)
    pr_projects = extract_pull_request_projects(extract_directory=extract_directory)
    return "\n".join([
        "| {name} | {type} | {project_count} | {multi_branch_projects} | {pr_projects} |".format(
            pr_projects="Yes" if set(v['projects']).intersection(pr_projects) else "No",
            multi_branch_projects="Yes" if set(v['projects']).intersection(multi_branch_projects) else "No",
            project_count=len(v['projects']),
            **v
        ) for v in devops_bindings.values()
    ])


def process_rules(extract_directory):
    template_rules = set()
    plugin_rules = set()
    for rule in object_reader(directory=extract_directory, key='getRules'):
        if rule.get('templateKey'):
            template_rules.add(rule['key'])
        if rule['repo'] not in BUILTIN_REPOS:
            plugin_rules.add(rule['key'])
    return template_rules, plugin_rules


def process_profile_rules(extract_directory, template_rules, plugin_rules):
    profiles = dict()
    for rule_dict in object_reader(directory=extract_directory, key='getProfileRules'):
        for rule_key, actives in rule_dict.items():
            if not isinstance(actives, list):
                continue
            template_rule = False
            plugin_rule = False
            if rule_key in template_rules:
                template_rule = True
            if rule_key in plugin_rules:
                plugin_rule = True
            for profile in actives:
                if profile['qProfile'] not in profiles.keys():
                    profiles[profile['qProfile']] = dict(plugin_rules=0, template_rules=0)
                if template_rule:
                    profiles[profile['qProfile']]['template_rules'] += 1
                if plugin_rule:
                    profiles[profile['qProfile']]['plugin_rules'] += 1
    return profiles


def format_pipelines(extract_directory):
    ci_mapping = dict()
    for analysis in object_reader(directory=extract_directory, key='getProjectAnalyses'):
        if 'detectedCI' not in analysis.keys():
            continue
        if analysis['detectedCI'] not in ci_mapping.keys():
            ci_mapping[analysis['detectedCI']] = dict(projects=set(), scans=0, first_scan=None, last_scan=None)
        ci_mapping[analysis['detectedCI']]['projects'].add(analysis['projectKey'])
        ci_mapping[analysis['detectedCI']]['scans'] += 1
        date = datetime.strptime(analysis['date'], '%Y-%m-%dT%H:%M:%S%z')
        if not ci_mapping[analysis['detectedCI']]['first_scan'] or date < ci_mapping[analysis['detectedCI']][
            'first_scan']:
            ci_mapping[analysis['detectedCI']]['first_scan'] = date
        if not ci_mapping[analysis['detectedCI']]['last_scan'] or date > ci_mapping[analysis['detectedCI']][
            'last_scan']:
            ci_mapping[analysis['detectedCI']]['last_scan'] = date

    return "\n".join([
        "| {name} | {project_count} | {first_scan} | {last_scan} | {total_scans} |".format(
            name=k,
            project_count=len(v['projects']),
            first_scan=v['first_scan'].strftime('%Y-%m-%d'),
            last_scan=v['last_scan'].strftime('%Y-%m-%d'),
            total_scans=v['scans']
        ) for k, v in ci_mapping.items()
    ])


def format_permission_templates(config):
    return "\n".join([
        "| {name} | {description} | {pattern} | {defaults} |".format(name=k, description=v.get('description', ""),
                                                                     pattern=v.get('pattern', ""),
                                                                     defaults=v.get('defaultFor', "")) for k, v in
        config.get('globalSettings', dict()).get('permissionTemplates', dict()).items()
    ])


def process_project_details(extract_directory):
    projects = list()
    profiles = defaultdict(int)
    gates = dict()
    for project in object_reader(directory=extract_directory, key='getProjectDetails'):
        for profile in project['qualityProfiles']:
            profiles[profile['key']] += 1
        if project['qualityGate']['name'] not in gates.keys():
            gates[project['qualityGate']['name']] = 0
        gates[project['qualityGate']['name']] += 1
        projects.append(
            dict(
                name=project['name'],
                key=project['key'],
                main_branch=project.get('branch', ''),
                profiles=[i['key'] for i in project['qualityProfiles'] if not i.get('deleted', False)],
                languages=set([i['language'] for i in project['qualityProfiles'] if not i.get('deleted', False)]),
                quality_gate=project['qualityGate']['key'],
                binding=project.get('binding', dict()).get('key', '')
            )
        )
    return projects, profiles, gates


def format_applications(extract_directory):
    return "\n".join(
        ["| {name} | {project_count} |".format(
            name=application['application']['name'],
            project_count=len(application['application']['projects'])
        ) for application in
            object_reader(directory=extract_directory, key='getApplicationDetails')])


def format_gates(gate_mapping):
    return "\n".join([
        "| {name} | {project_count} |".format(
            name=name,
            project_count=len(projects)
        ) for name, projects in gate_mapping.items() if name is not None
    ])


def load_server_info(extract_directory):
    info = [i for i in object_reader(directory=extract_directory, key='getServerInfo')][0]
    return info


def process_entity(extract_directory, entity_type, key='key'):
    entities = list()
    for entity in object_reader(directory=extract_directory, key=entity_type):
        entities.append(extract_path_value(path=key, obj=entity))
    return entities


def process_devops_bindings(extract_directory):
    devops_bindings = dict()
    for binding in object_reader(directory=extract_directory, key='getProjectBindings'):
        if binding['key'] not in devops_bindings.keys():
            devops_bindings[binding['key']] = dict(
                projects=[],
                name=binding['key'],
                type=binding['alm']
            )
        devops_bindings[binding['key']]['projects'].append(binding['projectKey'])
    return devops_bindings


def format_quality_gates(extract_directory, gate_mapping):
    return "\n".join(["| {name} | {project_count} |".format(
        name=gate['name'], project_count=gate_mapping.get(gate['name'], 0)) for gate in
        object_reader(directory=extract_directory, key='getGates') if not gate['isBuiltIn']]
    )



def process_plugins(extract_directory):
    return "\n".join(["| {name} | {description} | {version} | {url} |".format(
        name=plugin.get('name') if plugin.get('name') is not None else 'N/A',
        description=plugin.get('description') if plugin.get('description') is not None else 'N/A',
        version=plugin.get('version') if plugin.get('version') is not None else 'N/A',
        url=plugin.get('homepageUrl') if plugin.get('homepageUrl') is not None else 'N/A'
    ) for plugin in object_reader(directory=extract_directory, key='getPlugins') if
        "sonar" not in plugin.get('organizationName', '').lower()])


def process_permission_templates(extract_directory):
    default_templates = dict()
    MAPPING = dict(
        APP="Applications",
        TRK="Projects",
        VW="Portfolios"
    )
    for template in object_reader(directory=extract_directory, key='getDefaultTemplates'):
        if template['templateId'] not in default_templates.keys():
            default_templates[template['templateId']] = set()
        default_templates[template['templateId']].add(MAPPING[template['qualifier']])

    return "\n".join(["| {name} | {description} | {pattern} | {defaults} |".format(
        name=template['name'],
        description=template.get('description', ""),
        pattern=template.get('projectKeyPattern', ""),
        defaults=", ".join(default_templates.get(template['id'], []))
    ) for template in object_reader(directory=extract_directory, key='getTemplates')])


def format_plugins(extract_directory):
    return "\n".join(["| {name} | {description} | {version} | {url} |".format(name=plugin['name'],
                                                                              description=plugin['description'],
                                                                              version=plugin['version'],
                                                                              url=plugin['homepageUrl']) for plugin in
                      object_reader(directory=extract_directory, key='getPlugins') if
                      "sonar" not in plugin.get('organizationName', '').lower() and plugin['type'] != 'BUNDLED'])


def extract_selection_modes(portfolio):
    selection_modes = set()
    if portfolio.get('selectionMode'):
        selection_modes.add(portfolio['selectionMode'])
    for child in portfolio.get('subViews', list()):
        selection_modes = selection_modes.union(extract_selection_modes(portfolio=child))
    return selection_modes


def process_portfolios(extract_directory):
    portfolios = dict()
    for portfolio in object_reader(directory=extract_directory, key='getPortfolioDetails'):
        portfolios[portfolio['key']] = dict(
            name=portfolio['name'],
            projects=set(),
            selection=extract_selection_modes(portfolio=portfolio),
            children="Yes" if portfolio.get('subViews') else "No",
        )
    for project in object_reader(directory=extract_directory, key='getPortfolioProjects'):
        if project['portfolioKey'] not in portfolios.keys():
            continue
        portfolios[project['portfolioKey']]['projects'].add(project['key'])

    return "\n".join(["| {name} | {selection} | {children} | {project_count} |".format(
        project_count=len(portfolio['projects']),
        name=portfolio['name'],
        selection=','.join(portfolio['selection']),
        children=portfolio['children']
    ) for portfolio in portfolios.values()])


def format_quality_profiles(profile_mapping, extract_directory, profile_rules):
    profiles = list()
    for profile in object_reader(directory=extract_directory, key='getProfiles'):
        profiles.append(dict(
            language=profile['language'],
            name=profile['name'],
            is_built_in=profile.get('isBuiltIn', False),
            is_default="Yes" if profile.get('isDefault', False) else "No",
            parent=profile.get('parentName', ""),
            project_count=profile_mapping.get(profile['key'], 0),
            template_rules=profile_rules.get(profile['key'], dict()).get('template_rules', 0),
            plugin_rules=profile_rules.get(profile['key'], dict()).get('plugin_rules', 0)
        ))
    return "\n".join([
        "| {language} | {name} | {parent} | {is_default} | {template_rules} | {plugin_rules} | {project_count} |".format(
            **profile) for profile in profiles if not profile['is_built_in']])


def create_project_issues_dict():
    return dict(
        template_issues=0,
        plugin_issues=0,
        total_issues=0
    )




def format_project_metrics(projects, profile_rules):
    results = []
    for project in projects:
        details = dict(
            name=project['name'],
            plugin_rules = sum(
                [profile_rules.get(lang, dict()).get('plugin_rules', 0) for lang in project['profiles']]
            ),
            template_rules = sum(
                [profile_rules.get(lang, dict()).get('template_rules', 0) for lang in project['profiles']]
            ),
        )
        if details['plugin_rules'] + details['template_rules'] > 0:
            results.append(details)
    return "\n".join([
        "| {name} | {template_rules} | {plugin_rules} |".format(
            **project
        ) for project in results
    ])


def process_sast_config(extract_directory):
    sast = False
    for setting in object_reader(directory=extract_directory, key='getProjectSettings'):
        if 'security.conf' in setting['key'].lower():
            sast = True
            break
    return sast


def generate_markdown(extract_directory):
    with open(MARKDOWN_PATH, 'rt') as f:
        template_content = f.read()
    server_info = load_server_info(extract_directory=extract_directory)
    projects, profile_mapping, gate_mapping = process_project_details(extract_directory=extract_directory)
    user_count = process_entity(extract_directory=extract_directory, entity_type='getUsers', key='$.paging.total')
    template_rules, plugin_rules = process_rules(extract_directory=extract_directory)
    profile_rules = process_profile_rules(extract_directory=extract_directory, plugin_rules=plugin_rules,
                                          template_rules=template_rules)
    bindings = process_devops_bindings(extract_directory=extract_directory)

    md = template_content.format(
        server_version="{edition} {version}".format(
            edition=server_info['System']['Edition'],
            version=server_info['Application Nodes'][0]['System']['Version'] if server_info.get(
                'Application Nodes') else server_info['System']['Version']
        ),
        server_url=server_info['serverUrl'],
        project_count=len(projects),
        lines_of_code=sum(
            process_entity(extract_directory=extract_directory, entity_type='getUsage', key='$.linesOfCode')
        ),
        user_count=user_count[0] if user_count else 0,
        auth_method="",
        devops_bindings=format_devops_bindings(extract_directory=extract_directory, devops_bindings=bindings),
        pipelines=format_pipelines(extract_directory=extract_directory),
        permission_templates=process_permission_templates(extract_directory=extract_directory),
        quality_profiles=format_quality_profiles(profile_mapping=profile_mapping, extract_directory=extract_directory,
                                                 profile_rules=profile_rules),
        quality_gates=format_quality_gates(extract_directory=extract_directory, gate_mapping=gate_mapping),
        portfolios=process_portfolios(extract_directory=extract_directory),
        applications=format_applications(extract_directory=extract_directory),
        plugins=format_plugins(extract_directory=extract_directory),
        project_metrics=format_project_metrics(projects=projects, profile_rules=profile_rules),
        sast_configued="Yes" if process_sast_config(extract_directory=extract_directory) else "No",
    )
    with open(os.path.join(extract_directory, 'report.md'), 'wt') as f:
        f.write(md)
    return md

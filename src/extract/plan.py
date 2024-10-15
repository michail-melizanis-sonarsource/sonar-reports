import os
import json
ENTITY_DIR = os.path.join(os.path.dirname(__file__), '../entities/')

def get_available_entity_configs(server_version, edition):
    available_entities = dict()
    for root, dirs, files in os.walk(ENTITY_DIR):
        entity = root.split('/')[-1]
        latest_version = None
        for file in sorted(files):
            if not file.endswith('json'):
                continue
            file_version = float(file.replace('.json', ''))
            if file_version <= server_version and (latest_version is None or file_version > latest_version):
                latest_version = file_version
        if latest_version is None:
            continue
        with open(f'{ENTITY_DIR}/{entity}/{latest_version}.json', 'r') as f:
            config = json.load(f)
            if edition in config.get('editions', ['datacenter', 'developer', 'enterprise', 'community']) :
                available_entities[entity] = config
    return available_entities


def generate_extraction_plan(entities, entity_configs):
    extractions = set()
    for entity in entities:
        dependencies = extract_dependencies(entity=entity, entity_configs=entity_configs)
        if dependencies is None:
            continue
        extractions.add(entity)
        extractions = extractions.union(dependencies)
    return plan_extractions(extractions=extractions, entity_configs=entity_configs)


def extract_dependencies(entity, entity_configs):
    dependencies = set()
    entity_config = entity_configs.get(entity)
    if entity_config is None:
        return None
    for dependency in entity_config.get('dependencies', []):
        nested_dependencies = extract_dependencies(entity=dependency['key'], entity_configs=entity_configs)
        if nested_dependencies is None:
            dependencies = None
            break
        dependencies = dependencies.union(nested_dependencies)
        dependencies.add(dependency['key'])
    return dependencies


def plan_extractions(extractions: set, entity_configs: dict):
    completed = set()
    extraction_plan = list()
    continue_planning = True
    while continue_planning:
        phase = list()
        for extraction in extractions - completed:
            if completed >= set([i['key'] for i in entity_configs[extraction].get('dependencies', list())]):
                phase.append(extraction)
        completed = completed.union(set(phase))
        if not phase or len(completed) == len(extractions):
            continue_planning = False
        if phase:
            extraction_plan.append(phase)
    return extraction_plan

from collections import defaultdict
from utils import multi_extract_object_reader


def process_project_measures(directory, extract_mapping, server_id_mapping):
    measures = defaultdict(dict)
    for url, measure in multi_extract_object_reader(directory=directory, mapping=extract_mapping,
                                                    key='getProjectMeasures'):
        server_id = server_id_mapping[url]
        if measure['projectKey'] not in measures[server_id].keys():
            measures[server_id][measure['projectKey']] = dict(
                server_id=server_id,
                project_key=measure['projectKey'],
            )
        value = extract_measure_value(measure)
        if value is not None:
            measures[server_id][measure['projectKey']][measure['metric']] = value
    return measures

def extract_measure_value(measure):
    val = measure.get('value')
    if 'period' in measure.keys():
        val = extract_measure_value(measure['period'])
    return val

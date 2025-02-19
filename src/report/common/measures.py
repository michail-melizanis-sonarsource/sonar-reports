from collections import defaultdict

from parser import extract_path_value
from utils import multi_extract_object_reader


def process_project_measures(directory, extract_mapping, server_id_mapping):
    measures = defaultdict(lambda : defaultdict(lambda: dict(
        server_id=None,
        project_key=None
    )))
    for url, measure in multi_extract_object_reader(directory=directory, mapping=extract_mapping,
                                                    key='getProjectMeasures'):
        server_id = server_id_mapping[url]
        project_key = extract_path_value(obj=measure, path='$.projectKey')
        metric = extract_path_value(obj=measure, path='$.metric')
        measures[server_id][project_key].update(dict(
            server_id=server_id,
            project_key=project_key,
        ))
        value = extract_measure_value(measure)
        if metric is not None and value is not None:
            measures[server_id][project_key][metric] = value
    return measures

def extract_measure_value(measure):
    val = measure.get('value')
    if 'period' in measure.keys():
        val = extract_measure_value(measure['period'])
    return val

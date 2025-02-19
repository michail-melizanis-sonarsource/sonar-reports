from report.utils import generate_section


def generate_profile_summary(profile_map, languages):

    row = dict(
        profiles=0,
        active=0,
        sonar_way=0,
        custom_defaults=0
    )
    for server_id, language_profiles in profile_map.items():
        for language, profiles in language_profiles.items():
            if language not in languages.keys():
                continue
            for profile in profiles.values():
                row['profiles'] += 1
                if len(profile['projects']) > 0:
                    row['active'] += 1
                    if profile['root'] is not None and (profile['root'].lower() == 'sonar way' or profile['name'].lower() == 'sonar way'):
                        row['sonar_way'] += 1
                if not profile['is_built_in'] and profile['is_default'] == "Yes":
                    row['custom_defaults'] += 1

    return generate_section(
        title='Profiles',
        level=3,
        headers_mapping={
            "Total Profiles": "profiles",
            "Active Profiles": "active",
            "Active Profiles Inheriting from Sonar Way": "sonar_way",
            "Custom Default Profiles": "custom_defaults",
        },
        rows=[row]
    )
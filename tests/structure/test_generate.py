import unittest
from report.generate import process_plugins

class TestProcessPlugins(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_process_plugins_with_missing_data(self):
        extract_directory = 'test_directory'
        plugins = [
            {'name': 'Plugin1', 'description': 'Description1', 'version': '1.0', 'homepageUrl': 'http://example.com'},
            {'name': 'Plugin2', 'description': 'Description2', 'version': '2.0', 'homepageUrl': None},
            {'name': 'Plugin3', 'description': 'Description3', 'version': None},
            {'name': 'Plugin4', 'description': None, 'version': '4.0'},
            {'name': None, 'description': 'Description5', 'version': '5.0'},
            {}
        ]
        
        def mock_object_reader(directory, key):
            return plugins
        
        # Replace the object_reader function with the mock
        original_object_reader = process_plugins.__globals__['object_reader']
        process_plugins.__globals__['object_reader'] = mock_object_reader
        
        try:
            result = process_plugins(extract_directory)
            expected = (
                "| Plugin1 | Description1 | 1.0 | http://example.com |\n"
                "| Plugin2 | Description2 | 2.0 | N/A |\n"
                "| Plugin3 | Description3 | N/A | N/A |\n"
                "| Plugin4 | N/A | 4.0 | N/A |\n"
                "| N/A | Description5 | 5.0 | N/A |\n"
                "| N/A | N/A | N/A | N/A |"
            )
            self.assertEqual(result, expected)
        finally:
            # Restore the original object_reader function
            process_plugins.__globals__['object_reader'] = original_object_reader

if __name__ == '__main__':
    unittest.main()
from elasticsearch import Elasticsearch
from oceandb_driver_interface.utils import get_value
_DB_INSTANCE = None

def get_database_instance(config_file=None):
    global _DB_INSTANCE
    if _DB_INSTANCE is None:
        _DB_INSTANCE = ElasticsearchInstance(config_file)

    return _DB_INSTANCE

class ElasticsearchInstance(object):
    def __init__(self, config=None):
        host = get_value('db.hostname', 'DB_HOSTNAME', 'localhost', config)
        port = int(get_value('db.port', 'DB_PORT', 27017, config))
        username = get_value('db.username', 'DB_USERNAME', None, config)
        password = get_value('db.password', 'DB_PASSWORD', None, config)
        index = get_value('db.index', 'DB_INDEX', 'oceandb', config)
        self._index = index
        self._es = Elasticsearch(
            [host],
            http_auth=(username, password),
            port=port,
        )

    @property
    def instance(self):
        return self

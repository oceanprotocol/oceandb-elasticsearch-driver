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
        port = int(get_value('db.port', 'DB_PORT', 9200, config))
        username = get_value('db.username', 'DB_USERNAME', None, config)
        password = get_value('db.password', 'DB_PASSWORD', None, config)
        index = get_value('db.index', 'DB_INDEX', 'oceandb', config)
        ssl = get_value('db.ssl', 'DB_SSL', False, config)
        verify_certs = get_value('db.verifyCerts', 'DB_VERIFY_CERTS', False, config)
        ca_certs = get_value('db.caCertPath', 'DB_CA_CERTS', None, config)
        client_key = get_value('db.clientKey', 'DB_CLIENT_KEY', None, config)
        client_cert = get_value('db.clientCertPath', 'DB_CLIENT_CERT', None, config)

        self._index = index
        self._es = Elasticsearch(
            [host],
            http_auth=(username, password),
            port=port,
            use_ssl=ssl,
            verify_certs=verify_certs,
            ca_certs=ca_certs,
            client_cert=client_key,
            client_key=client_cert
        )

    @property
    def instance(self):
        return self

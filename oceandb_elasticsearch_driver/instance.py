#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

from elasticsearch import Elasticsearch
from oceandb_driver_interface.utils import get_value
from oceandb_elasticsearch_driver.mapping import mapping
import logging
import time

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
        ssl = self.str_to_bool(get_value('db.ssl', 'DB_SSL', 'false', config))
        verify_certs = self.str_to_bool(
            get_value('db.verify_certs', 'DB_VERIFY_CERTS', 'false', config)
        )
        ca_certs = get_value('db.ca_cert_path', 'DB_CA_CERTS', None, config)
        client_key = get_value('db.client_key', 'DB_CLIENT_KEY', None, config)
        client_cert = get_value('db.client_cert_path', 'DB_CLIENT_CERT', None, config)
        self._index = index
        try:
            self._es = Elasticsearch(
                [host],
                http_auth=(username, password),
                port=port,
                use_ssl=ssl,
                verify_certs=verify_certs,
                ca_certs=ca_certs,
                client_cert=client_key,
                client_key=client_cert,
                maxsize=1000
            )
            while self._es.ping() is False:
                logging.info("Trying to connect...")
                time.sleep(5)

            self._es.indices.create(index=index, ignore=400, body=mapping)

        except Exception as e:
            logging.info(f"Exception trying to connect... {e}")


    @property
    def es(self):
        return self._es

    @property
    def db_index(self):
        return self._index

    @property
    def instance(self):
        return self

    @staticmethod
    def str_to_bool(s):
        if s == 'true':
            return True
        elif s == 'false':
            return False
        else:
            raise ValueError

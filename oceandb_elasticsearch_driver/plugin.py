"""Implementation of OceanDB plugin based in Elasticsearch"""
from oceandb_driver_interface.plugin import AbstractPlugin
from oceandb_elasticsearch_driver.instance import get_database_instance
import logging

class Plugin(AbstractPlugin):
    """Elasticsearch ledger plugin for `Ocean DB's Python reference
    implementation <https://github.com/oceanprotocol/oceandb-elasticsearch-driver>`_.
    Plugs in a Elasticsearch instance as the persistence layer for Ocean Db
    related actions.
    """

    def __init__(self, config=None):
        """Initialize a :class:`~.Plugin` instance and connect to Elasticsearch.
        """
        self.driver = get_database_instance(config)
        self.logger = logging.getLogger('Plugin')
        logging.basicConfig(level=logging.INFO)

    @property
    def type(self):
        """str: the type of this plugin (``'Elasticsearch'``)"""
        return 'Elasticsearch'

    def write(self, obj, resource_id=None):
        if self.driver._es.exists(index=self.driver._index, id=resource_id, doc_type='_doc') == False:
            return self.driver._es.create(index=self.driver._index, id=resource_id, body=obj, doc_type='_doc', refresh='wait_for')

    def read(self, resource_id):
        return self.driver._es.get(index=self.driver._index, id=resource_id, doc_type='_doc')['_source']

    def update(self, obj, resource_id):
        return self.driver._es.index(index=self.driver._index, id=resource_id, body=obj, doc_type='_doc', refresh='wait_for')

    def delete(self, resource_id):
        if self.driver._es.exists(index=self.driver._index, id=resource_id, doc_type='_doc'):
            return self.driver._es.delete(index=self.driver._index, id=resource_id, doc_type='_doc')

    def list(self, search_from=None, search_to=None, offset=None, limit=None):
        body = {
            'sort': [
                { "_id" : "asc" },
            ],
            'query': {
                'match_all' : {}
            }
        }

        if search_from:
            body['from'] = search_from
        if search_to:
            body['size'] = search_to-search_from

        page = self.driver._es.search(
            index = self.driver._index,
            doc_type = '_doc',
            body = body
        )

        list = []
        for x in page['hits']['hits']:
          list.append(x['_source'])
        return list

    def query(self, query_string):
        print(query_string)
        body = {
            'sort': [
                { "_id" : "asc" },
            ]
        }

        print(body)
        page = self.driver._es.search(
            index = self.driver._index,
            doc_type = '_doc',
            body = body,
            q = query_string
        )

        list = []
        for x in page['hits']['hits']:
          list.append(x['_source'])
        return list

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
        """Write obj in elasticsearch.
        :param obj: value to be written in elasticsearch.
        :param resource_id: id for the resource.
        :return: id of the transaction.
        """
        self.logger.debug('elasticsearch::write::{}'.format(resource_id))
        if resource_id is not None:
            if self.driver._es.exists(
                index=self.driver._index,
                id=resource_id,
                doc_type='_doc'
            ):
                raise ValueError("Resource \"{}\" already exists, use update instead".format(resource_id))
        return self.driver._es.index(
            index=self.driver._index,
            id=resource_id,
            body=obj,
            doc_type='_doc',
            refresh='wait_for'
        )['_id']

    def read(self, resource_id):
        """Read object in elasticsearch using the resource_id.
        :param resource_id: id of the object to be read.
        :return: object value from elasticsearch.
        """
        self.logger.debug('elasticsearch::read::{}'.format(resource_id))
        return self.driver._es.get(
            index=self.driver._index,
            id=resource_id,
            doc_type='_doc'
        )['_source']

    def update(self, obj, resource_id):
        """Update object in elasticsearch using the resource_id.
        :param metadata: new metadata for the transaction.
        :param resource_id: id of the object to be updated.
        :return: id of the object.
        """
        self.logger.debug('elasticsearch::update::{}'.format(resource_id))
        return self.driver._es.index(
            index=self.driver._index,
            id=resource_id,
            body=obj,
            doc_type='_doc',
            refresh='wait_for'
        )['_id']

    def delete(self, resource_id):
        """Delete an object from elasticsearch.
        :param resource_id: id of the object to be deleted.
        :return:
        """
        self.logger.debug('elasticsearch::delete::{}'.format(resource_id))
        if self.driver._es.exists(
            index=self.driver._index,
            id=resource_id,
            doc_type='_doc'
        ) == False:
            raise ValueError("Resource \"{}\" does not exists".format(resource_id))
        return self.driver._es.delete(
            index=self.driver._index,
            id=resource_id,
            doc_type='_doc'
        )

    def list(self, search_from=None, search_to=None, limit=None):
        """List all the objects saved elasticsearch.
         :param search_from: start offset of objects to return.
         :param search_to: last offset of objects to return.
         :param limit: max number of values to be returned.
         :return: list with transactions.
         """
        self.logger.debug('elasticsearch::list')
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
        if limit:
            body['size'] = limit

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
        """Query elasticsearch for objects.
        :param query_string: query in string format.
        :return: list of objects that match the query.
        """
        self.logger.debug('elasticsearch::query::{}'.format(query_string))
        body = {
            'sort': [
                { "_id" : "asc" },
            ]
        }

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

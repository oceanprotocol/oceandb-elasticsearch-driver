"""Implementation of OceanDB plugin based in Elasticsearch"""
import logging

from oceandb_driver_interface.plugin import AbstractPlugin
from oceandb_driver_interface.search_model import FullTextModel, QueryModel

from oceandb_elasticsearch_driver.instance import get_database_instance
from oceandb_elasticsearch_driver.utils import query_parser


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
                raise ValueError(
                    "Resource \"{}\" already exists, use update instead".format(resource_id))
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
                {"_id": "asc"},
            ],
            'query': {
                'match_all': {}
            }
        }

        if search_from:
            body['from'] = search_from
        if search_to:
            body['size'] = search_to - search_from
        if limit:
            body['size'] = limit

        page = self.driver._es.search(
            index=self.driver._index,
            doc_type='_doc',
            body=body
        )

        object_list = []
        for x in page['hits']['hits']:
            object_list.append(x['_source'])
        return object_list

    def query(self, search_model: QueryModel):
        """Query elasticsearch for objects.
        :param search_model: object of QueryModel.
        :return: list of objects that match the query.
        """
        query_parsed = query_parser(search_model.query)
        self.logger.debug(f'elasticsearch::query::{query_parsed[0]}')
        if search_model.sort is not None:
            self._mapping_to_sort(search_model.sort.keys())
            sort = self._sort_object(search_model.sort)
        else:
            sort = [{"_id": "asc"}]
        if search_model.query == {}:
            query = {'match_all': {}}
        else:
            query = query_parsed[0]

        body = {
            'query': query,
            'sort': sort,
            'from': search_model.page * search_model.offset,
            'size': search_model.offset,
        }

        page = self.driver._es.search(
            index=self.driver._index,
            doc_type='_doc',
            body=body,
            q=query_parsed[1]
        )

        object_list = []
        for x in page['hits']['hits']:
            object_list.append(x['_source'])
        return object_list

    def text_query(self, search_model: FullTextModel):
        """Query elasticsearch for objects.
        :param search_model: object of FullTextModel
        :return: list of objects that match the query.
        """
        self.logger.debug('elasticsearch::text_query::{}'.format(search_model.text))
        if search_model.sort is not None:
            self._mapping_to_sort(search_model.sort.keys())
            sort = self._sort_object(search_model.sort)
        else:
            sort = [{"service.metadata.curation.rating": "asc"}]
        body = {
            'sort': sort,
            'from': search_model.page * search_model.offset,
            'size': search_model.offset,
        }

        page = self.driver._es.search(
            index=self.driver._index,
            doc_type='_doc',
            body=body,
            q=search_model.text
        )

        object_list = []
        for x in page['hits']['hits']:
            object_list.append(x['_source'])
        return object_list

    def _mapping_to_sort(self, keys):
        for i in keys:
            mapping = """{
                              "properties": {
                                "%s" : { 
                                  "type": "text",
                                  "fields": {
                                    "keyword": { 
                                      "type": "keyword"
                                    }
                                  }
                                }
                              }
                        }
            """ % i
            if self.driver._es.indices.get_field_mapping(i)[self.driver._index]['mappings'] == {}:
                self.driver._es.indices.put_mapping(index=self.driver._index, body=mapping,
                                                    doc_type='_doc')

    def _sort_object(self, sort):
        try:
            o = []
            for i in sort.keys():
                if self.driver._es.indices.get_field_mapping(i)[self.driver._index]['mappings'][
                    '_doc'][i]['mapping'][i.split('.')[-1]]['type'] == 'text':
                    o.append({i + ".keyword": ('asc' if sort.get(i) == 1 else 'desc')}, )
                else:
                    o.append({i: ('asc' if sort.get(i) == 1 else 'desc')}, )
            return o
        except Exception:
            raise Exception("Sort \"{}\" does not have a valid format.".format(sort))

"""Implementation of OceanDB plugin based in Elasticsearch"""
#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

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
            if self.driver.es.exists(
                    index=self.driver.db_index,
                    id=resource_id,
                    doc_type='_doc'
            ):
                raise ValueError(
                    "Resource \"{}\" already exists, use update instead".format(resource_id))

        return self.driver.es.index(
            index=self.driver.db_index,
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
        return self.driver.es.get(
            index=self.driver.db_index,
            id=resource_id,
            doc_type='_doc'
        )['_source']

    def update(self, obj, resource_id):
        """Update object in elasticsearch using the resource_id.
        :param obj: new value
        :param resource_id: id of the object to be updated.
        :return: id of the object.
        """
        self.logger.debug('elasticsearch::update::{}'.format(resource_id))
        return self.driver.es.index(
            index=self.driver.db_index,
            id=resource_id,
            body=obj,
            doc_type='_doc',
            refresh='wait_for'
        )['_id']

    def delete_all(self):
        q = '''{
            "query" : {
                "match_all" : {}
            }
        }'''
        self.driver.es.delete_by_query('_all', q)

    def delete(self, resource_id):
        """Delete an object from elasticsearch.
        :param resource_id: id of the object to be deleted.
        :return:
        """
        self.logger.debug('elasticsearch::delete::{}'.format(resource_id))
        if not self.driver.es.exists(
                index=self.driver.db_index, id=resource_id, doc_type='_doc'):
            raise ValueError(f"Resource {resource_id} does not exists")
        return self.driver.es.delete(
            index=self.driver.db_index,
            id=resource_id,
            doc_type='_doc'
        )

    def count(self):
        count_result = self.driver.es.count(index=self.driver.db_index)
        if count_result is not None and count_result['count'] > 0:
            return count_result['count']

        return 0

    def list(self, search_from=None, search_to=None, limit=None):
        """List all the objects saved in elasticsearch

         :param search_from: start offset of objects to return.
         :param search_to: last offset of objects to return.
         :param limit: max number of values to be returned.
         :return: generator with all matching documents
         """
        self.logger.debug('elasticsearch::list')
        _body = {
            'sort': [
                {"_id": "asc"},
            ],
            'query': {
                'match_all': {}
            }
        }

        count = 0
        count_result = self.driver.es.count(index=self.driver.db_index)
        if count_result is not None and count_result['count'] > 0:
            count = count_result['count']

        if not count:
            return []

        search_from = search_from if search_from is not None and search_from >= 0 else 0
        search_from = min(search_from, count-1)
        search_to = search_to if search_to is not None and search_to >= 0 else (count-1)
        limit = search_to - search_from + 1
        chunk_size = min(25, limit)

        _body['size'] = chunk_size
        processed = 0
        while processed < limit:
            body = _body.copy()
            body['from'] = search_from
            result = self.driver.es.search(
                index=self.driver.db_index,
                body=body
            )
            hits = result['hits']['hits']
            search_from += len(hits)
            processed += len(hits)
            for x in hits:
                yield x['_source']

    def query(self, search_model: [QueryModel, FullTextModel]):
        """Query elasticsearch for objects.
        :param search_model: object of QueryModel.
        :return: list of objects that match the query.
        """
        assert search_model.page >= 1, 'page value %s is invalid' % search_model.page
        if isinstance(search_model, FullTextModel):
            return self.text_query(search_model)

        text = None
        query = search_model.query
        if 'text' in query:
            text = query.pop('text')

        query_parsed = query_parser(search_model.query)
        self.logger.debug(f'elasticsearch::query::{query_parsed}')
        if search_model.sort is not None:
            self._mapping_to_sort(search_model.sort.keys())
            sort = self._sort_object(search_model.sort)
        else:
            sort = [{"_id": "asc"}]

        if text:
            sort = [{"_score": "desc"}] + sort
            if isinstance(text, str):
                text = [text]
            text = [t.strip() for t in text]
            text = [t.replace('did:op:', '0x') for t in text if t]

        if search_model.query == {}:
            query = {'match_all': {}}
        else:
            query = query_parsed

        body = {
            'sort': sort,
            'from': (search_model.page - 1) * search_model.offset,
            'size': search_model.offset,
            'query': query
        }

        page = self.driver.es.search(
            index=self.driver.db_index,
            body=body,
            q=text or None
        )

        object_list = []
        for x in page['hits']['hits']:
            object_list.append(x['_source'])
        return object_list, page['hits']['total']

    def text_query(self, search_model: FullTextModel):
        """Query elasticsearch for objects.
        :param search_model: object of FullTextModel
        :return: list of objects that match the query.
        """
        assert search_model.page >= 1, 'page value %s is invalid' % search_model.page
        self.logger.debug('elasticsearch::text_query::{}'.format(search_model.text))
        if search_model.sort is not None:
            self._mapping_to_sort(search_model.sort.keys())
            sort = self._sort_object(search_model.sort)
        else:
            sort = [{"service.attributes.curation.rating": "asc"}]
        body = {
            'sort': sort,
            'from': (search_model.page - 1) * search_model.offset,
            'size': search_model.offset,
        }

        page = self.driver.es.search(
            index=self.driver.db_index,
            body=body,
            q=search_model.text
        )

        object_list = []
        for x in page['hits']['hits']:
            object_list.append(x['_source'])
        return object_list, page['hits']['total']

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
            if self.driver.es.indices.get_field_mapping(i)[self.driver.db_index]['mappings'] == {}:
                self.driver.es.indices.put_mapping(index=self.driver.db_index, body=mapping, doc_type='_doc')

    def _sort_object(self, sort):
        try:
            o = []
            for key in sort.keys():
                last_k = key.split('.')[-1]
                field_mapping = self.driver.es.indices.get_field_mapping(key)
                value = field_mapping[self.driver.db_index]['mappings']['_doc'][key]['mapping'][last_k]['type']
                if value == 'text':
                    o.append({key + ".keyword": ('asc' if sort.get(key) == 1 else 'desc')}, )
                else:
                    o.append({key: ('asc' if sort.get(key) == 1 else 'desc')}, )
            return o
        except Exception:
            raise Exception("Sort \"{}\" does not have a valid format.".format(sort))

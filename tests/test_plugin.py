from datetime import datetime, timedelta

import pytest
from oceandb_driver_interface.oceandb import OceanDb
from oceandb_driver_interface.search_model import FullTextModel, QueryModel

from oceandb_elasticsearch_driver.utils import query_parser
from .ddo_example import ddo_sample

es = OceanDb('./tests/oceandb.ini').plugin


def test_plugin_type_is_es():
    assert es.type == 'Elasticsearch'


def test_write_without_id():
    object_id = es.write({"value": "test"})
    es.delete(object_id)


def test_write_error():
    with pytest.raises(
            ValueError,
            message="Resource \"1\" already exists, use update instead"
    ):
        es.write({"value": "test"}, 1)
        es.write({"value": "test"}, 1)
    es.delete(1)


def test_delete_error():
    with pytest.raises(
            ValueError,
            message="Resource \"abc\" does not exists"
    ):
        es.delete("abc")


def test_plugin_write_and_read():
    es.write({"value": "test"}, 1)
    assert es.read(1)['value'] == 'test'
    es.delete(1)


def test_update():
    es.write({"value": "test"}, 1)
    assert es.read(1)['value'] == 'test'
    es.update({"value": "testUpdated"}, 1)
    assert es.read(1)['value'] == 'testUpdated'
    es.delete(1)


def test_plugin_list():
    es.write({"value": "test1"}, 1)
    es.write({"value": "test2"}, 2)
    es.write({"value": "test3"}, 3)
    es.write({"value": "test4"}, 4)
    es.write({"value": "test5"}, 5)
    es.write({"value": "test6"}, 6)
    assert len(es.list()) == 6
    assert es.list()[0]['value'] == 'test1'
    es.delete(1)
    assert len(es.list(search_from=2, search_to=4)) == 2
    assert es.list(search_from=3, search_to=5)[1]['value'] == 'test5'
    assert es.list(search_from=1, limit=2)[0]['value'] == 'test2'
    es.delete(2)
    es.delete(3)
    es.delete(4)
    es.delete(5)
    es.delete(6)


# def test_query():
#     es.write({"value": "test1"}, 1)
#     es.write({"value": "test2"}, 2)
#     es.write({"value": "test3"}, 3)
#     es.write({"value": "foo"}, 4)
#     es.write({"value": "foo"}, 5)
#     es.write({"value": "test6"}, 6)
#     search_model = QueryModel({"value": "foo"}, {"value": 1})
#     assert len(es.query(search_model)) == 2
#     es.delete(1)
#     es.delete(2)
#     es.delete(3)
#     es.delete(4)
#     es.delete(5)
#     es.delete(6)


def test_search_query():
    es.write(ddo_sample, ddo_sample['id'])
    search_model = QueryModel({'price': [0, 12]})
    assert es.query(search_model)[0]['id'] == ddo_sample['id']
    search_model_2 = QueryModel({'license': ['CC-BY']})
    assert es.query(search_model_2)[0]['id'] == ddo_sample['id']
    search_model_3 = QueryModel({'price': [0, 12], 'license': ['CC-BY']})
    assert es.query(search_model_3)[0]['id'] == ddo_sample['id']
    search_model_4 = QueryModel(
        {'price': [0, 12], 'license': ['CC-BY'], 'type': ['Access', 'Metadata']})
    assert es.query(search_model_4)[0]['id'] == ddo_sample['id']
    search_model_5 = QueryModel({'sample': []})
    assert es.query(search_model_5)[0]['id'] == ddo_sample['id']
    search_model_6 = QueryModel({'created': ['today']})
    assert len(es.query(search_model_6)) == 0
    search_model_7 = QueryModel({'created': []})
    assert es.query(search_model_7)[0]['id'] == ddo_sample['id']
    es.delete(ddo_sample['id'])


def test_full_text_query():
    es.write({"value": "test1"}, 1)
    es.write({"value": "test2"}, 2)
    es.write({"value": "test3"}, 3)
    es.write({"value": "foo4"}, 4)
    es.write({"value": "foo5"}, 5)
    es.write({"value": "test6"}, 6)
    search_model = FullTextModel('foo?', {'value': 1}, offset=6, page=0)
    assert len(es.text_query(search_model)) == 2
    es.delete(1)
    es.delete(2)
    es.delete(3)
    es.delete(4)
    es.delete(5)
    es.delete(6)


def test_full_text_query_tree():
    es.write({"father": {"son": "test1"}}, 1)
    es.write({"father": {"son": "test2"}}, 2)
    es.write({"father": {"son": "test3"}}, 3)
    es.write({"father": {"son": "foo4"}}, 4)
    es.write({"father": {"son": "foo5"}}, 5)
    es.write({"father": {"son": "test6"}}, 6)
    search_model = FullTextModel('foo?', {'father.son': -1}, offset=6, page=0)
    assert len(es.text_query(search_model)) == 2
    assert es.text_query(search_model)[0]['father']['son'] == 'foo5'
    es.delete(1)
    es.delete(2)
    es.delete(3)
    es.delete(4)
    es.delete(5)
    es.delete(6)


def test_query_parser():
    query = {'price': [0, 10]}
    assert query_parser(query) == {
        "bool": {"must": [{"range": {"service.metadata.base.price": {"gte": 0, "lte": 10}}}]}}
    query = {'price': [15]}
    assert query_parser(query) == {
        "bool": {"must": [{"range": {"service.metadata.base.price": {"gte": 0, "lte": 15}}}]}}
    query = {'license': ['CC-BY']}
    assert query_parser(query) == {
        "bool": {"should": [{"match": {"service.metadata.base.license": "CC-BY"}}]}}
    query = {'type': ['Access', 'Metadata']}
    assert query_parser(query) == {"bool": {"must": [{"match": {"service.type": "Access"}},
                                                     {"match": {"service.type": "Metadata"}}]}}
    query = {'price': [0, 10], 'type': ['Access', 'Metadata']}
    assert query_parser(query) == {
        "bool": {"must": [{"range": {"service.metadata.base.price": {"gte": 0, "lte": 10}}},
                          {"match": {"service.type": "Access"}},
                          {"match": {"service.type": "Metadata"}}]}}

    query = {'license': []}
    assert query_parser(query) == {}
    query = {'license': [], 'type': ['Access', 'Metadata']}
    assert query_parser(query) == {"bool": {"must": [{"match": {"service.type": "Access"}},
                                                     {"match": {"service.type": "Metadata"}}]}}
    query = {'license': ['CC-BY'], 'type': ['Access', 'Metadata']}
    assert query_parser(query) == {"bool": {
        "should": [
            {"match": {"service.metadata.base.license": "CC-BY"}}
        ],
        "must": [
            {"match": {"service.type": "Access"}},
            {"match": {"service.type": "Metadata"}}
        ]
    }}
    query = {'created': ['today', 'lastWeek', 'lastMonth', 'lastYear']}
    assert query_parser(query)['bool']['must'][0]['range']['created']['gte'].year == (
            datetime.now() - timedelta(days=365)).year
    query = {'created': ['no_valid']}
    assert query_parser(query)['bool']['must'][0]['range']['created']['gte'].year == (
            datetime.now() - timedelta(weeks=1000)).year
    query = {'categories': ['weather', 'other']}
    assert query_parser(query) == {"bool": {
        "should": [{"match": {"service.metadata.base.categories": "weather"}},
                   {"match": {"service.metadata.base.categories": "other"}}]}}

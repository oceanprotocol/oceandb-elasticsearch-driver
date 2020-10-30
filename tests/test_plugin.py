#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0
import time
import pytest
from oceandb_driver_interface.oceandb import OceanDb
from oceandb_driver_interface.search_model import FullTextModel, QueryModel

from oceandb_elasticsearch_driver.utils import query_parser
from .ddo_example import ddo_sample

es = OceanDb('./tests/oceandb.ini').plugin


def delete_all():
    result = es.driver.es.search(index=es.driver.db_index, body={'size': 1000})
    records = result['hits']['hits']
    for doc in records:
        _id = doc['_id']
        try:
            es.delete(_id)
        except Exception as e:
            print(e)


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
    delete_all()
    count = 27
    for i in range(count):
        try:
            es.write({f"value{i}": f"test{i}"}, i)
        except ValueError as e:
            print(f'resource already exist: {i} <error>: {e}')

    assert len(list(es.list())) == count
    assert list(es.list())[0]['value0'] == 'test0'
    es.delete(0)
    time.sleep(2)
    assert len(list(es.list())) == count-1
    result = list(es.list(search_from=2, search_to=4))
    assert len(result) == 3
    result = list(es.list(search_from=3, search_to=5))
    assert result[1]['value13'] == 'test13'
    result = list(es.list(search_from=1, limit=2))
    assert result[0]['value10'] == 'test10'
    for i in range(1, count):
        es.delete(i)


def test_search_query():
    delete_all()
    es.write(ddo_sample, ddo_sample['id'])
    search_model = QueryModel({'cost': ["0", "12"]})
    assert es.query(search_model)[0][0]['id'] == ddo_sample['id']
    search_model_2 = QueryModel({'license': ['CC-BY']})
    assert es.query(search_model_2)[0][0]['id'] == ddo_sample['id']
    search_model_3 = QueryModel({'cost': ["0", "12"], 'license': ['CC-BY']})
    assert es.query(search_model_3)[0][0]['id'] == ddo_sample['id']
    search_model_4 = QueryModel(
        {'cost': ["0", "12"], 'license': ['CC-BY'], 'metadata_type': ['dataset']})
    assert es.query(search_model_4)[0][0]['id'] == ddo_sample['id']
    search_model_5 = QueryModel({'sample': []})
    assert es.query(search_model_5)[0][0]['id'] == ddo_sample['id']
    search_model_6 = QueryModel({'created': ['2016-02-07T16:02:20Z', '2016-02-09T16:02:20Z']})
    assert len(es.query(search_model_6)[0]) == 1
    search_model_7 = QueryModel({'dateCreated': ['2016-02-07T16:02:20Z', '2016-02-09T16:02:20Z']})
    assert es.query(search_model_7)[0][0]['id'] == ddo_sample['id']
    search_model_8 = QueryModel({'datePublished': ['2016-02-07T16:02:20Z', '2016-02-09T16:02:20Z']})
    assert len(es.query(search_model_8)[0]) == 1
    search_model_9 = QueryModel(
        {'datePublished': ['2016-02-07T16:02:20Z', '2016-02-09T16:02:20Z'], 'text': ['Weather']})
    assert len(es.query(search_model_9)[0]) == 1
    search_model_10 = QueryModel({'text': ['Weather']})
    assert len(es.query(search_model_10)[0]) == 1
    assert len(es.query(QueryModel({'text': ['UK']}))[0]) == 1
    assert len(es.query(QueryModel({'text': ['uk']}))[0]) == 1
    assert len(es.query(QueryModel({'text': ['uK']}))[0]) == 1
    assert len(es.query(QueryModel({'text': ['2015']}))[0]) == 0
    assert len(es.query(QueryModel({'text': ['2011']}))[0]) == 1
    assert len(es.query(QueryModel({'text': ['2011', 'uuuukkk', 'temperature']}))[0]) == 1

    assert len(es.query(QueryModel({'service.attributes.additionalInformation.customField': ['customValue']}))[0]) == 1
    assert len(es.query(QueryModel({'service.attributes.additionalInformation.nonExistentField': ['customValue']}))[0]) == 0

    search_model = QueryModel({'cost': ["0", "12"], 'text': ['Weather']})
    assert es.query(search_model)[0][0]['id'] == ddo_sample['id']

    search_model_dataToken = QueryModel({'dataToken': ['0x2eD6d94Ec5Af12C43B924572F9aFFe470DC83282']})
    assert len(es.query(search_model_dataToken)[0]) == 1

    es.delete(ddo_sample['id'])


def test_full_text_query():
    es.write({"value": "test1"}, 1)
    es.write({"value": "test2"}, 2)
    es.write({"value": "test3"}, 3)
    es.write({"value": "foo4"}, 4)
    es.write({"value": "foo5"}, 5)
    es.write({"value": "test6"}, 6)
    search_model = FullTextModel('foo?', {'value': 1}, offset=6, page=1)
    assert len(es.text_query(search_model)) == 2
    es.delete(1)
    es.delete(2)
    es.delete(3)
    es.delete(4)
    es.delete(5)
    es.delete(6)


def test_full_text_query_tree():

    def delete_ids(ids, mult=1):
        for i in ids:
            try:
                es.delete(i*mult)
            except Exception:
                pass
    delete_ids(range(1, 7))
    delete_ids(range(1, 8), 10)

    es.write({"father": {"son": "test1"}}, 1)
    es.write({"father": {"son": "test2"}}, 2)
    es.write({"father": {"son": "test3"}}, 3)
    es.write({"father": {"son": "foo4"}}, 4)
    es.write({"father": {"son": "foo5"}}, 5)
    es.write({"father": {"son": "test6"}}, 6)
    search_model = FullTextModel('foo?', {'father.son': -1}, offset=6, page=1)
    results = es.text_query(search_model)[0]
    assert len(results) == 2
    assert results[0]['father']['son'] == 'foo5'

    # test sorting by numbers
    es.write({"price": {"value": 1, "ocean": 2.3, "pool": "0x1"}}, 10)
    es.write({"price": {"value": 2, "ocean": 2.3, "pool": "0x2"}}, 20)
    es.write({"price": {"value": 3, "ocean": 2.3, "pool": "0x3"}}, 30)
    es.write({"price": {"value": 11, "ocean": 2.3, "pool": "0x11"}}, 40)
    es.write({"price": {"value": 12, "ocean": 2.3, "pool": "0x12"}}, 50)
    es.write({"price": {"value": 13, "ocean": 2.3, "pool": "0x13"}}, 60)
    es.write({"price": {"value": 4, "ocean": 2.3, "pool": "0x4"}}, 70)
    search_model = FullTextModel('0x*', {'price.value': 1})  # ascending
    results = es.text_query(search_model)[0]
    assert len(results) == 7, ''
    values = [r["price"]["value"] for r in results]
    assert values == [1, 2, 3, 4, 11, 12, 13]

    search_model = FullTextModel('0x*', {'price.pool': 1})
    results = es.text_query(search_model)[0]
    assert len(results) == 7, ''
    pools = [r["price"]["pool"] for r in results]
    assert pools == ["0x1", "0x11", "0x12", "0x13", "0x2", "0x3", "0x4"]

    delete_ids(range(1, 7))
    delete_ids(range(1, 8), 10)


def test_query_parser():
    query = {'cost': ["0", "100"]}
    assert query_parser(query) == ({"bool": {"must": [{"bool": {"should": [{"range": {"service.attributes.main.cost": {"gte": "0", "lte": "100"}}}]}}]}})

    query = {'cost': ["15"]}
    assert query_parser(query) == ({"bool": {"must": [{"bool": {"should": [{"match": {"service.attributes.main.cost": "15"}}]}}]}})

    query = {'license': ['CC-BY']}
    assert query_parser(query) == ({"bool": {"must": [{"bool": {"should": [{"match": {"service.attributes.main.license": "CC-BY"}}]}}]}})

    query = {'metadata_type': ['dataset', 'algorithm']}
    assert query_parser(query) == ({
        "bool": {"must": [{
            "bool": {
                "should": [
                    {"match": {"service.attributes.main.type": "dataset"}},
                    {"match": {"service.attributes.main.type": "algorithm"}}
                ]}
        }]}
    })

    query = {'type': ['Access', 'Metadata']}
    assert query_parser(query) == ({"bool": {"must": [{"bool": {"should": [{"match": {"service.type": "Access"}}, {"match": {"service.type": "Metadata"}}]}}]}})

    query = {'cost': ["0", "10"], 'type': ['Access', 'Metadata']}
    assert query_parser(query) == ({
            "bool": {
                "must": [
                    {"bool": {"should": [{"range": {"service.attributes.main.cost": {"gte": "0", "lte": "10"}}}]}},
                    {"bool": {"should": [{"match": {"service.type": "Access"}}, {"match": {"service.type": "Metadata"}}]}}
                ]
            }
    })

    query = {'license': []}
    assert query_parser(query) == ({"bool": {"must": [{"bool": {"should": []}}]}})

    query = {'license': [], 'type': ['Access', 'Metadata']}
    assert query_parser(query) == ({
        "bool": {
            "must": [
                {"bool": {"should": []}},
                {"bool": {"should": [
                    {"match": {"service.type": "Access"}},
                    {"match": {"service.type": "Metadata"}}]}}
            ]}
    })

    query = {'license': ['CC-BY'], 'type': ['Access', 'Metadata']}
    assert query_parser(query) == ({
        "bool": {
            "must": [
                {"bool": {"should": [{"match": {"service.attributes.main.license": "CC-BY"}}]}},
                {"bool": {"should": [
                    {"match": {"service.type": "Access"}},
                    {"match": {"service.type": "Metadata"}}]}}
            ]}
    })

    query = {'license': ['CC-BY'], 'created': ['2016-02-07T16:02:20Z', '2016-02-09T16:02:20Z']}
    assert query_parser(query)["bool"]["must"][1]["bool"]["should"][0]["range"]["created"]["gte"].year == 2016

    query = {'datePublished': ['2017-02-07T16:02:20Z', '2017-02-09T16:02:20Z']}
    assert query_parser(query)["bool"]["must"][0]["bool"]["should"][0]["range"]["service.attributes.main.datePublished"]["gte"].year == 2017

    query = {'categories': ['weather', 'other']}
    assert query_parser(query) == ({"bool": {"must": [{"bool": {"should": [{"match": {"service.attributes.additionalInformation.categories": "weather"}}, {"match": {"service.attributes.additionalInformation.categories": "other"}}]}}]}})

    query = {'service.attributes.additionalInformation.customField': ['customValue']}
    assert query_parser(query) == ({"bool": {"must": [{"bool": {"should": [{"match": {"service.attributes.additionalInformation.customField": "customValue"}}]}}]}})

    query = {'service.attributes.additionalInformation.customNumber': [2, 5]}
    assert query_parser(query) == ({"bool": {"must": [{"bool": {"should": [{"range": {"service.attributes.additionalInformation.customNumber": {"gte": 2, "lte": 5}}}]}}]}})


def test_default_sort():
    es.write(ddo_sample, ddo_sample['id'])
    ddo_sample2 = ddo_sample.copy()
    ddo_sample2['id'] = 'did:op:cb36cf78d87f4ce4a784f17c2a4a694f19f3fbf05b814ac6b0b7197163888864'
    ddo_sample2['service'][2]['attributes']['curation']['rating'] = 0.99
    es.write(ddo_sample2, ddo_sample2['id'])
    search_model = QueryModel({'cost': [0, 12]})
    assert es.query(search_model)[0][0]['id'] == ddo_sample2['id']
    es.delete(ddo_sample['id'])
    es.delete(ddo_sample2['id'])

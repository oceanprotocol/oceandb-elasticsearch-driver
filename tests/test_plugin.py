import pytest
from oceandb_driver_interface.search_model import QueryModel, FullTextModel

from oceandb_driver_interface.oceandb import OceanDb

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


def test_query():
    es.write({"value": "test1"}, 1)
    es.write({"value": "test2"}, 2)
    es.write({"value": "test3"}, 3)
    es.write({"value": "foo"}, 4)
    es.write({"value": "foo"}, 5)
    es.write({"value": "test6"}, 6)
    search_model = QueryModel({"value": "foo"}, {"value": 1})
    assert len(es.query(search_model)) == 2
    es.delete(1)
    es.delete(2)
    es.delete(3)
    es.delete(4)
    es.delete(5)
    es.delete(6)


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

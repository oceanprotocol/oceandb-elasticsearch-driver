#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

import logging
from datetime import datetime

import oceandb_elasticsearch_driver.indexes as indexes

logger = logging.getLogger(__name__)

MUST = "must"
SHOULD = "should"
RANGE = "range"
BOOL = "bool"
FUZZY = "fuzzy"
MATCH = "match"
GTE = "gte"
LTE = "lte"


def query_parser(query):
    query_must = []
    key_to_index_and_maker = {
        'text': (None, create_text_query),
        'license': (indexes.license, create_query),
        'categories': (indexes.categories, create_query),
        'tags': (indexes.tags, create_query),
        'metadata_type': (indexes.metadata_type, create_query),
        'service_type': (indexes.service_type, create_query),
        'type': (indexes.service_type, create_query),
        'updateFrequency': (indexes.updated_frequency, create_query),
        'sample': (indexes.sample, create_query),
        'created': (indexes.created, create_time_query),
        'dataToken': (indexes.dataToken, create_query),
        'dateCreated': (indexes.dateCreated, create_time_query),
        'datePublished': (indexes.datePublished, create_time_query),
        'cost': (indexes.cost, create_number_query)
    }
    for key, value in query.items():
        if key not in key_to_index_and_maker:
            index = key
            if isinstance(value[0], int) or isinstance(value[0], float):
                query_maker = create_number_query
            else:
                query_maker = create_query
        else:
            index, query_maker = key_to_index_and_maker[key]

        if index is not None:
            query_must = query_maker(query_must, index, value)
        else:
            query_must = query_maker(query_must, value)

    query_result = {
        BOOL: {
            MUST: query_must
        }
    }
    return query_result


def create_time_query(query_must, index, value):
    if value[0] is None or value[1] is None:
        logger.warning("You should provide two dates in your query.")

    if value[0] > value[1]:
        logger.warning("Your second date is smaller that the first.")

    query_should = [{
        RANGE: {
            index: {
                GTE: datetime.strptime(value[0], '%Y-%m-%dT%H:%M:%SZ'),
                LTE: datetime.strptime(value[1], '%Y-%m-%dT%H:%M:%SZ')
            }
        }
    }]
    query_must.append({
        BOOL: {
            SHOULD: query_should
        }
    })
    return query_must


def create_text_query(query_must, value):
    query_should = []
    assert isinstance(value, str) or isinstance(value, (list, tuple, set)), \
        f'Invalid type of text search term, expected str or list of str, got {type(value)}'

    if not isinstance(value, (list, tuple, set)):
        value = [value]

    for i in range(len(value)):
        query_should.append({MATCH: {indexes.name: value[i]}})
        query_should.append({MATCH: {indexes.description: value[i]}})
    query_must.append({BOOL: {SHOULD: query_should}})
    return query_must


def create_query(query_must, index, value):
    query_should = []
    for i in range(len(value)):
        query_should.append({MATCH: {index: value[i]}})
    query_must.append({BOOL: {SHOULD: query_should}})
    return query_must


def create_number_query(query_must, index, value):
    query_should = []
    if len(value) > 2:
        logger.info('You are sending more values than needed.')
    elif len(value) == 0:
        logger.info('You are not sending any value.')
    elif len(value) == 1:
        query_should.append({
            MATCH: {
                index: value[0]
            }
        })
    else:
        query_should.append({
            RANGE: {
                index: {
                    GTE: value[0],
                    LTE: value[1]
                }
            }
        })
    query_must.append({
        BOOL: {
            SHOULD: query_should
        }
    })
    print(query_must)
    return query_must

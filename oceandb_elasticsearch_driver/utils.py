#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

import logging
from datetime import datetime

import oceandb_elasticsearch_driver.indexes as index

logger = logging.getLogger(__name__)

AND = 'must'
OR = 'should'
GT = 'gte'
LT = 'lte'
BOOL = 'bool'
RANGE = 'range'
MATCH = 'match'


def query_parser(query):
    query_result = {}
    text = None
    for key in query.items():
        if 'price' in key:
            query_result = create_price_query(query, query_result)
        elif 'license' in key:
            query_result = create_query(query['license'], index.license, query_result, OR, MATCH)
        elif 'categories' in key:
            query_result = create_query(query['categories'], index.categories, query_result, OR,
                                        MATCH)
        elif 'tags' in key:
            query_result = create_query(query['tags'], index.tags, query_result, OR,
                                        MATCH)
        elif 'type' in key:
            query_result = create_query(query['type'], index.service_type, query_result, AND, MATCH)
        elif 'updateFrequency' in key:
            query_result = create_query(query['updateFrequency'], index.updated_frequency,
                                        query_result, OR, MATCH)
        elif 'created' in key:
            query_result = create_created_query(query, query_result, 'created')
        elif 'dateCreated' in key:
            query_result = create_created_query(query, query_result, 'dateCreated')
        elif 'datePublished' in key:
            query_result = create_created_query(query, query_result, 'datePublished')
        elif 'sample' in key:
            query_result = create_query(['sample'], index.sample, query_result, AND, MATCH)
        elif 'text' in key:
            text = query['text'][0]
        else:
            logger.error('The key %s is not supported by OceanDB.' % key[0])
            raise Exception('The key %s is not supported by OceanDB.' % key[0])
    return query_result, text


def create_query(value, index, query, operator, query_type):
    for i in range(len(value)):
        if i == 0:
            if BOOL in query and operator in query[BOOL]:
                query[BOOL][operator] += [{query_type: {index: value[i]}}]
            else:
                if BOOL not in query:
                    query[BOOL] = {}
                query[BOOL][operator] = [{query_type: {index: value[i]}}]
        else:
            query[BOOL][operator] += [{query_type: {index: value[i]}}]
    return query


def create_price_query(query, query_result):
    if len(query['price']) > 2:
        logger.info('You are sending more values than needed.')
    elif len(query['price']) == 0:
        logger.info('You are not sending any value.')
    elif len(query['price']) == 1:
        query_result = create_query([{GT: 0, LT: query['price'][0]}], index.price, query_result,
                                    AND, RANGE)
    else:
        query_result = create_query([{GT: query['price'][0], LT: query['price'][1]}], index.price,
                                    query_result, AND, RANGE)
    return query_result


def create_created_query(query, query_result, field):
    if query[field][0] is None or query[field][1] is None:
        logger.warning("You should provide two dates in your query.")
    if query[field][0] > query[field][1]:
        logger.warning("Your second date is smaller that the first.")
    if field == 'created':
        query_result = create_query([{GT: datetime.strptime(query[field][0], '%Y-%m-%dT%H:%M:%SZ'),
                                      LT: datetime.strptime(query[field][1],
                                                            '%Y-%m-%dT%H:%M:%SZ')}], index.created,
                                    query_result, AND, RANGE)
    if field == 'dateCreated':
        query_result = create_query([{GT: datetime.strptime(query[field][0], '%Y-%m-%dT%H:%M:%SZ'),
                                      LT: datetime.strptime(query[field][1],
                                                            '%Y-%m-%dT%H:%M:%SZ')}],
                                    index.dateCreated,
                                    query_result,
                                    AND, RANGE)
    if field == 'datePublished':
        query_result = create_query([{GT: datetime.strptime(query[field][0], '%Y-%m-%dT%H:%M:%SZ'),
                                      LT: datetime.strptime(query[field][1],
                                                            '%Y-%m-%dT%H:%M:%SZ')}],
                                    index.datePublished, query_result,
                                    AND, RANGE)
    else:
        logger.info('The key %s is not supported in the created query')
    return query_result

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
RANGE = "range"
MATCH = "match"
GTE = "gte"
LTE = "lte"

def query_parser(query):
    query_must = []
    for key in query.items():
        if 'text' in key:
            query_must = create_text_query(query_must, query['text'])
        elif 'license' in key: 
            query_must = create_query(query_must, indexes.license, query['license'])
        elif 'categories' in key:
            query_must = create_query(query_must, indexes.categories, query['categories'])
        elif 'tags' in key:
            query_must = create_query(query_must, indexes.tags, query['tags'])
        elif 'type' in key:
            query_must = create_query(query_must, indexes.service_type, query['type'])
        elif 'updateFrequency' in key:
            query_must = create_query(query_must, indexes.updated_frequency, query['updateFrequency'])
        elif 'sample' in key:
            query_must = create_query(query_must, indexes.sample, query['sample'])
        elif 'created' in key:
            query_must = create_time_query(query_must, indexes.created, query['created'])
        elif 'dateCreated' in key:
            query_must = create_time_query(query_must, indexes.dateCreated, query['dateCreated'])
        elif 'datePublished' in key:
            query_must = create_time_query(query_must, indexes.datePublished, query['datePublished'])
        elif 'price' in key:
            query_must = create_price_query(query_must, query['price'])
        else:
            logger.error('The key %s is not supported by OceanDB.' % key[0])
            raise Exception('The key %s is not supported by OceanDB.' % key[0])
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
    query_should = []
    query_should.append({RANGE: {index: { GTE: datetime.strptime(value[0], '%Y-%m-%dT%H:%M:%SZ'), LTE: datetime.strptime(value[1], '%Y-%m-%dT%H:%M:%SZ')}}})
    query_must.append({BOOL: {SHOULD: query_should}})
    return query_must

def create_text_query(query_must, value):
    query_should = []
    for i in range(len(value)):
        query_should.append({FUZZY: {indexes.name: value[i]}})
        query_should.append({FUZZY: {indexes.description: value[i]}})
    query_must.append({BOOL: {SHOULD: query_should}})
    return query_must

def create_query(query_must, index ,value):
    query_should = []
    for i in range(len(value)):
        query_should.append({MATCH: {index: value[i]}})
    query_must.append({BOOL: {SHOULD: query_should}})
    return query_must

def create_price_query(query_must, value):
    query_should = []
    if len(value) > 2:
        logger.info('You are sending more values than needed.')
    elif len(value) == 0:
        logger.info('You are not sending any value.')
    elif len(value) == 1:
        query_should.append({MATCH: {indexes.price: value[0]}})
    else:
        query_should.append({RANGE: {indexes.price: { GTE: value[0], LTE: value[1]}}})
    query_must.append({BOOL: {SHOULD: query_should}})
    return query_must
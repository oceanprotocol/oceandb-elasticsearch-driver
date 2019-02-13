import logging
from datetime import datetime, timedelta

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
    for key in query.items():
        if 'price' in key:
            if len(query['price']) > 2:
                logger.info('You are sending more values than needed.')
            elif len(query['price']) == 0:
                logger.info('You are not sending any value.')
            elif len(query['price']) == 1:
                query_result = {
                    BOOL: {AND: [{RANGE: {index.price: {GT: 0, LT: query['price'][0]}}}]}}
            else:
                query_result = {BOOL: {
                    AND: [{RANGE: {index.price: {GT: query['price'][0], LT: query['price'][1]}}}]}}
        elif 'license' in key:
            query_result = create_query(query['license'], index.license, query_result, OR)
        elif 'categories' in key:
            query_result = create_query(query['categories'], index.categories, query_result, OR)
        elif 'type' in key:
            query_result = create_query(query['type'], index.service_type, query_result, AND)
        elif 'updateFrequency' in key:
            query_result = create_query(query['updateFrequency'], index.updated_frequency,
                                        query_result, OR)
        elif 'created' in key:
            now = datetime.now() - timedelta(weeks=1000)
            for values in query['created']:
                if values == 'today':
                    now = datetime.now() - timedelta(days=1)
                elif values == 'lastWeek':
                    now = datetime.now() - timedelta(days=7)
                elif values == 'lastMonth':
                    now = datetime.now() - timedelta(days=30)
                elif values == 'lastYear':
                    now = datetime.now() - timedelta(days=365)
                else:
                    logger.info('The key %s is not supported in the created query' % values)
            query_result = {BOOL: {AND: [{RANGE: {index.created: {GT: now}}}]}}
        elif 'sample' in key:
            query_result = {MATCH: {index.sample: 'sample'}}
        else:
            logger.error('The key %s is not supported by OceanDB.' % key[0])
            raise Exception('The key %s is not supported by OceanDB.' % key[0])
    return query_result


def create_query(value, index, query, operator):
    for i in range(len(value)):
        if i == 0:
            if BOOL in query and operator in query[BOOL]:
                query[BOOL][operator] += [{MATCH: {index: value[i]}}]
            else:
                if BOOL not in query:
                    query[BOOL] = {}
                query[BOOL][operator] = [{MATCH: {index: value[i]}}]
        else:
            query[BOOL][operator] += [{MATCH: {index: value[i]}}]
    return query

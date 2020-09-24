#!coding:utf-8

import address

import pymysql
import redis


def mysql_connect(config):
    port = int(address.oss_mysql_config["port"])
    if 'port' in config:
        port = int(config['port'])
    return pymysql.connect(
        host=config['host'],
        port=port,
        user=config['user'],
        password=config['password'],
        database=config['database'],
        charset='utf8'
    )


def redis_connect(config):
    return redis.Redis(
        host=config['host'],
        port=config['port'],
        password=config['password'],
        db=config['database']
    )


def rollback_quietly(backable):
    if backable is not None:
        backable.rollback()


def close_quietly(closable):
    if closable is not None:
        closable.close()

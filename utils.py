# -*- coding: utf-8 -*
import pika
from configparser import ConfigParser
import oss2
import redis


class DataSaver(object):
    """
    存储图片的对象
    """
    def do_save(self, file, file_path):
        raise NotImplementedError


class LocalFile(DataSaver):
    def __init__(self, config_path):
        cfg = ConfigParser
        cfg.read(config_path)
        self.basic_path = cfg.get('saver', 'root_path')

    def do_save(self, file, file_path):
        pass


class AliBucket(DataSaver):
    def __init__(self, config_path):
        cfg = ConfigParser()
        cfg.read(config_path)
        auth = oss2.Auth(cfg.get('oss', 'auth_id'), cfg.get('oss', 'auth_key'))
        self.bucket = oss2.Bucket(auth, cfg.get('oss', 'bucket_domain'),
                                  cfg.get('oss', 'bucket_name'))

    def do_save(self, file, file_path):
        self.bucket.put_object(file_path, file)


class Cacher(object):
    """
    读取缓存的对象
    """
    def set_cache(self, key, value, ex):
        raise NotImplementedError

    def exists(self, key):
        raise NotImplementedError


class RedisCache(Cacher):
    def __init__(self, config_path):
        cfg = ConfigParser()
        cfg.read(config_path)
        if cfg.getint('app', 'debug') == 1:
            self.rd = redis.StrictRedis(host=cfg.get('redis', 'host'), port=cfg.get('redis', 'port'))
        else:
            self.rd = redis.StrictRedis(host=cfg.get('redis', 'host'),
                                        port=cfg.get('redis', 'port'),
                                        password=cfg.get('redis', 'passwd'))

    def set_cache(self, key, value, ex):
        self.rd.set(key, value, ex=ex)

    def exists(self, key):
        return self.rd.exists(key)


class MQNormal:
    def __init__(self, cfg):
        self.host = cfg.get('mq', 'host')
        self.user = cfg.get('mq', 'user')
        self.password = cfg.get('mq', 'password')

    def start_mq(self):
        credentials = pika.PlainCredentials(self.user, self.password)
        param = pika.ConnectionParameters(
            host=self.host,
            heartbeat=60,
            # blocked_connection_timeout=60,
            credentials=credentials
        )
        return pika.BlockingConnection(param)

    def start_mq_debug(self):
        param = pika.ConnectionParameters(
            host=self.host,
            heartbeat=5,
            # blocked_connection_timeout=10
        )
        return pika.BlockingConnection(param)

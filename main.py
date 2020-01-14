from configparser import ConfigParser
import argparse
import importlib
import string
# from multiprocessing import Process
from utils import AliBucket, RedisCache, MQNormal


def camel_string(s):
    au = s.split("_")
    n = ""
    for sub in au:
        n = n + string.capwords(sub)

    return n


def start_consumer(cfg, args):
    model = args['model']
    # import wisdom 下的类名(识别方法类)
    mod = importlib.import_module('models.' + model + '.' + model)
    # 获取类名
    main_class = getattr(mod, camel_string(model))
    ins = main_class(model)
    # 设置告警图片存储介质
    ins.set_saver(AliBucket(args['config']))
    # 设置缓存兑现
    ins.set_cacher(RedisCache(args['config']))

    # 队列
    if args['queue'] == 'default':
        args['queue'] = model

    if cfg.getint('app', 'debug') == 1:
        mq = MQNormal(cfg).start_mq_debug()
    else:
        mq = MQNormal(cfg).start_mq()

    chan = mq.channel()
    chan.basic_qos(prefetch_count=1)
    chan.queue_declare(queue=args['queue'], arguments={'x-message-ttl': cfg.getint('mq', 'ttl')})
    chan.basic_consume(queue=args['queue'], on_message_callback=ins.callback)
    print("Start consuming...")
    try:
        chan.start_consuming()

    except KeyboardInterrupt or ConnectionResetError:
        chan.stop_consuming()
        mq.close()


if __name__ == '__main__':
    # python3 main.py -q [model-name]
    ap = argparse.ArgumentParser()
    # 你想要监听的队列
    ap.add_argument("-q", "--queue", default="default", help="the queue you wanna listen")
    # 你想要指定使用的识别模型
    ap.add_argument("-m", "--model", required=True, help="select a model")
    # 配置文件位置
    ap.add_argument("-c", "--config", default="config.ini", help="config path")
    # 命令行配置
    a = vars(ap.parse_args())
    # 环境变量
    c = ConfigParser()
    c.read(a['config'])
    models = c.get('app', 'models').split(",")

    start_consumer(c, a)








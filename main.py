from configparser import ConfigParser
import argparse
import importlib
import string
from utils import AliBucket, RedisCache, MQNormal

if __name__ == '__main__':
    # python3 consume.py -q [model-name]
    ap = argparse.ArgumentParser()
    ap.add_argument("-q", "--queue", required=True, help="the queue you wanna listen")
    ap.add_argument("-m", "--model", required=True, help="select the model")
    ap.add_argument("-c", "--config", default="config.ini", help="config path")
    args = vars(ap.parse_args())
    cfg = ConfigParser()
    cfg.read(args['config'])

    # import wisdom 下的类名(识别方法类)
    mod = importlib.import_module('models.' + args['model'] + '.' + args['model'])
    # 获取类名
    main_class = getattr(mod, string.capwords(args['model']))
    ins = main_class(args['model'])
    # 设置告警图片存储介质
    ins.set_saver(AliBucket(args['config']))
    # 设置缓存兑现
    ins.set_cacher(RedisCache(args['config']))

    # 队列
    if cfg.getint('app', 'debug') == 1:
        mq = MQNormal(cfg).start_mq_debug()
    else:
        mq = MQNormal(cfg).start_mq()

    chan = mq.channel()
    chan.basic_qos(prefetch_count=1)
    chan.queue_declare(queue=args['queue'], arguments={'x-message-ttl': 120000})
    chan.basic_consume(queue=args['queue'], on_message_callback=ins.callback)
    print("Start consuming...")
    try:
        chan.start_consuming()

    except KeyboardInterrupt or ConnectionResetError:
        chan.stop_consuming()
        mq.close()





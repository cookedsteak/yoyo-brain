# -*- coding: utf-8 -*
import os
import cv2
import time
import numpy as np
from utils import DataSaver, Cacher
import darknet as dn


class Wisdom(object):
    saver = None
    cacher = None

    def callback(self, ch, method, properties, body):
        raise NotImplementedError

    def after_callback(self, ch, load, frame, frame_cropped):
        """
        回调图像违规后的操作，分为：
        1. 存储图像
        2. 放入通知队列
        :param ch:
        :param load:
        :param frame:
        :param frame_cropped:
        :return:
        """
        raise NotImplementedError

    def check_alarm(self, key, ex_time):
        if self.cacher.exists(key):
            return True
        else:
            self.cacher.set_cache(key, 1, ex=ex_time)
            return False

    def save_alarm(self, file, path):
        date_time = time.strftime("%Y-%m-%d", time.localtime())
        file = cv2.imencode('.jpg', file)[1].tostring()
        tmp_name = str(time.time())
        img_name = tmp_name.replace(".", "_")
        file_path = path + date_time + "/" + img_name + ".jpg"
        self.saver.do_save(file, file_path)
        return file_path

    @staticmethod
    def send_alarm(ch, body):
        key_name = 'squirtle'
        ch.exchange_declare(exchange=key_name, exchange_type='direct')
        ch.queue_declare(key_name)
        ch.queue_bind(queue=key_name, exchange=key_name, routing_key=key_name)
        ch.basic_publish(exchange=key_name, routing_key=key_name, body=body)

    def set_cacher(self, cacher):
        if isinstance(cacher, Cacher):
            self.cacher = cacher
        else:
            raise ValueError

    def set_saver(self, saver):
        if isinstance(saver, DataSaver):
            self.saver = saver
        else:
            raise ValueError

    @staticmethod
    def get_dn_net(a):
        """
        获得 darknet 神经网路
        :param a:
        :return:
        """
        # 获得脚本的真实目录而不是执行目录
        # getcwd 是获取工作目录
        path = os.path.split(os.path.realpath(__file__))[0]
        file_list = os.listdir(path + '/' + a)

        data_path = ""
        weights_path = ""
        config_path = ""

        for i in file_list:
            ext = os.path.splitext(i)[-1]
            if ext == ".data":
                data_path = os.path.sep.join([path, a, i])
            elif ext == ".weights":
                weights_path = os.path.sep.join([path, a, i])
            elif ext == ".cfg":
                config_path = os.path.sep.join([path, a, i])
            else:
                continue

        if data_path == "" or weights_path == "" or config_path == "":
            raise SystemExit("missing yolo file")

        net = dn.load_net(bytes(config_path, encoding="utf8"), bytes(weights_path, encoding="utf8"), 0)
        meta = dn.load_meta(bytes(data_path, encoding="utf8"))

        return net, meta

    @staticmethod
    def get_net(a):
        """
        准备 model_name 对应的神经网络
        :param a:
        :return:
        """
        # 获得脚本的真实目录而不是执行目录
        # getcwd 是获取工作目录
        path = os.path.split(os.path.realpath(__file__))[0]
        file_list = os.listdir(path + '/' + a)

        labels_path = ""
        weights_path = ""
        config_path = ""

        for i in file_list:
            ext = os.path.splitext(i)[-1]
            if ext == ".names":
                labels_path = os.path.sep.join([path, a, i])
            elif ext == ".weights":
                weights_path = os.path.sep.join([path, a, i])
            elif ext == ".cfg":
                config_path = os.path.sep.join([path, a, i])
            else:
                continue

        if labels_path == "" or weights_path == "" or config_path == "":
            raise SystemExit("missing yolo file")

        # print(config_path, weights_path)
        net = cv2.dnn.readNetFromDarknet(config_path, weights_path)
        net.setPreferableTarget(1)
        ln = net.getLayerNames()
        ln = [ln[i[0] - 1] for i in net.getUnconnectedOutLayers()]

        return net, ln, labels_path

    @staticmethod
    def loop_layer(lo, c, ww, hh, additional):
        """
        循环 中心点与宽高，返回标记框
        :param lo:
        :param c:
        :param ww:
        :param hh:
        :param additional: 额外的判断逻辑，以class_id作为参数
        :return:
        """
        bx = []  # boxes
        cf = []  # confidences
        cs = []  # classIds
        # loop over each of the layer outputs
        # lo 3个 ndarray
        for output in lo:
            # loop over each of the detections
            # detection (5+classes) * 507 的 2d array
            for detection in output:
                scores = detection[5:]
                # 分数最高的class
                class_id = np.argmax(scores)
                confidence = scores[class_id]

                if confidence > c and additional(class_id):
                    # 自动兑换盒子的比例
                    box = detection[0:4] * np.array([ww, hh, ww, hh])
                    (centerX, centerY, width, height) = box.astype("int")
                    # (centerX, centerY, width, height) = box

                    x = int(centerX - (width / 2))
                    y = int(centerY - (height / 2))

                    # 标记坐标加入盒子
                    bx.append([x, y, int(width), int(height)])
                    cf.append(float(confidence))
                    cs.append(class_id)

        return bx, cf, cs

    @staticmethod
    def decode_frame(data, info):
        array = np.reshape(data, newshape=info)
        # 如果没有 dtype这一步，可能出现
        # (-215:Assertion failed) func != 0 in function 'cv::hal::resize' 的错误
        return np.array(array, dtype=np.uint8)

    @staticmethod
    def decode_frame_tolist(data):
        return np.asarray(data)


    @staticmethod
    def crop_frame(W, H, x, y, w, h, frame):
        # 安全截取图片
        if h >= H:
            YY = H
        else:
            YY = h
        if w >= W:
            XX = W
        else:
            XX = w

        frame_cropped = frame[y:YY, x:XX]

        if len(frame_cropped) < 100:
            frame_cropped = frame

        return frame_cropped

    @staticmethod
    def array_to_image(arr):
        arr = arr.transpose(2, 0, 1)
        c = arr.shape[0]
        h = arr.shape[1]
        w = arr.shape[2]
        arr = (arr / 255.0).flatten()
        data = dn.c_array(dn.c_float, arr)
        im = dn.IMAGE(w, h, c, data)
        return im

    @staticmethod
    def draw_boxes(img, result, threshold):
        index = 0
        for objection in result:
            index += 1
            class_name, class_score, (x, y, w, h) = objection
            if class_score < threshold:
                continue

            left = int(x - w / 2)
            right = int(x + w / 2)
            top = int(y - h / 2)
            bottom = int(y + h / 2)

            cv2.rectangle(img, (left, top), (right, bottom), (0, 0, 255), 1)
            text = "{}: {:.4f}".format(class_name, class_score)
            cv2.putText(img, text, (int(x), int(y - 5)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

        return img

    @staticmethod
    def rgbgr_image(img):
        dn.rgbgr_image(img)

    @staticmethod
    def detect(net, meta, img):
        return dn.detect2(net, meta, img)
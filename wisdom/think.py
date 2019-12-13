from . import wisdom
import cv2
import json


class Think(wisdom.Wisdom):
    # 识别后不用进行处理的类别
    class_white_list = ['normal_people', 'normal_car', 'normal_tree']

    def __init__(self, model_name, queue_name):
        self.queue_name = queue_name
        self.net, self.meta = self.get_dn_net(model_name)

    def callback(self, ch, method, properties, body):
        load = json.loads(body.decode('utf-8'))
        # load['class_name'] = self.queue_name
        # 所接受到的数组升维
        frame = self.decode_frame(load["data"], info=load["info"])

        # 获取图像宽高
        (H, W) = frame.shape[:2]
        threshold = load["threshold"] / 100
        im = self.array_to_image(frame)
        self.rgbgr_image(im)

        # 初步检测结果
        result = self.detect(self.net, self.meta, im)

        # 这里的识别逻辑请自行添加
        # 以下是示范
        for objection in result:
            class_name, class_score, (x, y, w, h) = objection
            print(class_score, bytes.decode(class_name), threshold)
            if class_score < threshold or bytes.decode(class_name) in self.class_white_list:
                continue

            left = int(x - w / 2)
            right = int(x + w / 2)
            top = int(y - h / 2)
            bottom = int(y + h / 2)

            cv2.rectangle(frame, (left, top), (right, bottom), self.COLOR_RED, 1)
            text = "{}: {:.4f}".format(bytes.decode(class_name), class_score)
            cv2.putText(frame, text, (left, top), cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.RED, 1)

            frame_cropped = self.crop_frame(W, H, left, top, right, bottom, frame)
            self.after_callback(ch, load, frame, frame_cropped)
            print(class_name, class_score)

    def after_callback(self, ch, load, frame, frame_cropped):
        # 检查一定时间内是否已经提示过
        if self.check_alarm(str(load['id']) + '_' + load['class_name'], ex_time=self.time_range):
            return
from models import wisdom
import json


class SendMessage(wisdom.Wisdom):

    def __init__(self, model_name):
        self.net, self.meta = self.get_dn_net(model_name)

    def callback(self, ch, method, properties, body):
        # load包含了所有传递过来的消息、画面数组
        load = json.loads(body.decode('utf-8'))
        # 所接受到的数组升维
        frame = self.decode_frame(load["data"], info=load["info"])

        # 获取图像宽高
        (H, W) = frame.shape[:2]
        # 识别阈值
        threshold = load["threshold"] / 100
        # 转换成可识别数据
        im = self.array_to_image(frame)
        self.rgbgr_image(im)

        # 初步检测结果
        result = self.detect(self.net, self.meta, im)

        # 这里的识别逻辑请自行添加
        # 以下是示范
        for objection in result:
            class_name, class_score, (x, y, w, h) = objection
            print(class_score, bytes.decode(class_name), threshold)
            #
            #
            # Your own code here......
            #
            #

        ch.basic_ack(delivery_tag=method.delivery_tag)

    def after_callback(self, ch, load, frame, frame_cropped):
        # 消费者消费完后的处理逻辑
        # 下面是示例：保存截屏
        try:
            self.save_alarm(frame_cropped, load['save_path'])
        except Exception:
            raise Exception

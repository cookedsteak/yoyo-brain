# 说明

models 中的的模型和对应的业务逻辑代码存放在"以模型命名"的文件夹中。

```
models
    |--modelA
           |--classes.names  【识别类文件】
           |--my.data        【所以文件】
           |--yolov3.cfg     【模型配置文件】
           |--yolov3.weights 【模型文件】   
           |--modelA.py      【业务逻辑（继承Wisdom类）】  
    |--modelB
           |--...
           ...
```
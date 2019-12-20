# 说明

models 中的的模型和对应的业务逻辑代码存放在"以模型命名"的文件夹中。

```
models
    |--modelA
           |--classes.names  【识别类文件】
           |--my.data        【所以文件】
           |--yolov3.cfg     【模型配置文件】
           |--yolov3.weights 【模型文件】   
           |--logic.py      【业务逻辑（继承Wisdom类）】  
    |--modelB
           |--...
           ...
```

# 约束

每个模型中的 `logic.py` 是具体的识别业务逻辑。
需要保证的是【`logic.py`中的模型类名必须与models下的该文件名相同(首字母大写)】。
比如，模型文件夹名字为 modelA，则 `logic.py` 中的 class 就是 ModelA。


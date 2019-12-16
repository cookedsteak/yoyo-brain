# About

# Prerequisite

# Architecture
```
      scenario
  +--------------------------+
  |                          v
  |  +----------+  frame   +------------+     +------------+  message   +--------+
  |  | yoyo-eye | -------> |    AMQP    | --> | yoyo-mouth | ---------> | client |
  |  +----------+          +------------+     +------------+            +--------+
  |                          |
  |                          |
  |                          v
  |                        +------------+
  +----------------------- | yoyo-brain |
                           +------------+

```

# Strategy of model usage

# *Help
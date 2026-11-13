# 用 set_entry_point("A") 设置入口

from typing import TypedDict
from langgraph.graph import StateGraph, START, END

### 1. 定义状态
class State(TypedDict):
    content: str

### 2. 初始化/构建图
graph_builder = StateGraph(State)   #⭐括号内上传第一步定义的类
    #构件图和添加节点函数顺序没有强制要求

### 3. 添加节点函数
def node_a(state: State) -> State:
    return {"content": "处理完成"}

### 4、往图中添加节点
graph_builder.add_node("A", node_a)

### 5、 连边
graph_builder.add_edge("A", END)

### 6、 设置入口（必选）
graph_builder.set_entry_point("A")

#出口这里用 END 全局常量，无需额外 set_finish_point

### 7. 编译图
graph = graph_builder.compile()

### 8. 执行
res = graph.invoke({"content": "start"})
print(res)
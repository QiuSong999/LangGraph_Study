"""
LangGraph Reducer函数演示 - operator.add Reducer（列表追加）
"""
#普通列表追加拼接

import operator
from typing import Annotated, List
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
## 1、定义State状态类
"""operator.add Reducer（列表追加）"""
class ListAddState(TypedDict):
    # data: Annotated[List[int], None]      #等价于最初写的data:List[int],都是采用默认覆盖策略
    # Annotated 的第二个参数（Reducer）设置为 None，或者干脆不写第二个参数，LangGraph 就会采用默认的更新策略默认是覆盖
    data: Annotated[List[int], operator.add]    # ⭐operator.add （列表追加）

## 2、定义节点Node(就是干活的函数)
def producer_1(state: ListAddState) -> dict:
    print(f"初始---",state)   #输出：初始--- {'data': [0]}
    return {"data": [1, 2]}

def producer_2(state: ListAddState) -> dict:
    return {"data": [3, 4]}


## 3、定义一个总函数，包括了构建图graph、添加Node、Edge,编译图
def run_demo():
    builder = StateGraph(ListAddState)
    # 注册节点
    builder.add_node("producer1", producer_1)
    builder.add_node("producer2", producer_2)
    # 顺序执行边
    builder.add_edge(START, "producer1")
    builder.add_edge("producer1", "producer2")
    builder.add_edge("producer2", END)

    graph = builder.compile()
    result = graph.invoke({"data": [0]})
    print(f"执行结果: {result}\n")


if __name__ == "__main__":
    run_demo()

# 初始--- {'data': [0]}
# 执行结果: {'data': [0, 1, 2, 3, 4]}








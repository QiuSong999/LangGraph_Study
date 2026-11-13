"""
LangGraph Reducer函数演示 - 数值累加Reducer
"""

import operator
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

### 1、定义State状态类
""" 数值累加Reducer """
class NumberAddState(TypedDict):
    count: Annotated[int, operator.add]     #⭐

### 2、定义节点Node(就是干活的函数)
def increment_1(state: NumberAddState) -> dict:
    return {"count": 5}


def increment_2(state: NumberAddState) -> dict:
    return {"count": 3}

## 3、定义一个总函数，包括了构建图graph、添加Node、Edge,编译图
def run_demo():
    print("数值累加Reducer演示:")
    builder = StateGraph(NumberAddState)                    #构造图
    builder.add_node("increment_1", increment_1)            #添加节点
    builder.add_node("increment_2", increment_2)
    # 顺序执行边
    builder.add_edge(START, "increment_1")          #添加边
    builder.add_edge("increment_1", "increment_2")
    builder.add_edge("increment_2", END)

    graph = builder.compile()       #编译图

    result = graph.invoke({"count": 10})
    print(f"初始状态: {{'count': 10}}")
    print(f"执行结果: {result}\n")


if __name__ == "__main__":
    run_demo()
    """
    数值累加Reducer演示:
    初始状态: {'count': 10}
    执行结果: {'count': 18}
    """

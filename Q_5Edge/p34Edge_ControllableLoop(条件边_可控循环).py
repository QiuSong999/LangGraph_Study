#节点 a 和节点 b 交替执行，直到计数达到上限或被递归限制强制终止

from typing import Annotated, Dict, Literal
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.errors import GraphRecursionError

### 1、 定义状态机
class LoopState(TypedDict):
    count: int
    result: str
    max_count: int

### 2、 定义节点函数
#节点a
def node_a(state: LoopState) -> dict:
    """节点a：处理逻辑并更新计数"""
    print(f"执行节点a，当前计数: {state['count']}")
    return {
        'count': state['count'] + 1,
        'result': f"已处理{state['count']}次"
    }

#节点b
def node_b(state: LoopState) -> dict:
    """节点b：辅助处理"""
    print(f"执行节点b，当前计数: {state['count']}")
    return {
        'result': f"已处理{state['count']}次 - 辅助处理"
    }

# 条件判断节点（路由函数）
def route(state: LoopState) -> Literal["b", END]:
    """条件路由函数：决定是继续循环还是终止"""
    # 终止条件：当计数达到最大值时终止
    if state['count'] >= state['max_count']:
        print(f"满足终止条件，计数 {state['count']} >= {state['max_count']}，返回END")
        return END
    else:
        print(f"未满足终止条件，计数 {state['count']} < {state['max_count']}，返回b")
        return "b"

### 3、 创建图
builder = StateGraph(LoopState)

### 4、 添加节点     （条件判断节点不用添加）
builder.add_node("a", node_a)
builder.add_node("b", node_b)

### 5、 添加边
builder.add_edge(START, "a")    #节点 a 执行完毕，图引擎不会盲目去找下一个节点，而是专门去调用 route 函数
builder.add_conditional_edges("a", route)   #route里面有END，满足条件会结束
#END 不是通过 add_edge 添加的，而是通过 route 函数的返回值触发的
builder.add_edge("b", "a")      #如果上一步节点a未结束，设置到b
"""
builder.add_conditional_edges("a", route)
含义：只要节点 a 执行完毕，图引擎不会盲目去找下一个节点，而是专门去调用 route 函数。
此时：route 函数拿到了最新的 state（里面包含了 a 更新后的 count）。
判断：route 函数发现 count < max_count，于是返回了字符串 "b"。

根据返回值跳转到 b
因为 route 返回了 "b"，LangGraph 收到了这个指令，它就知道了：“哦，下一步应该去执行名为 "b" 的节点。”
于是图引擎顺着这个“路标”，去执行 builder.add_node("b", node_b) 里的 node_b 函数。

builder.add_edge("b", "a")
含义：只要节点 b 执行完毕，无条件直接回到节点 a

就这样，a与b节点函数交替执行
"""

### 6、 编译图
graph = builder.compile()

### 7、 执行图
print("=== 开始执行工作流 ===")
try:                                    #需要同时传多个参数，且顺序容易搞混时。写上参数名
    result = graph.invoke(input={       #input是 invoke() 的第一个位置参数，位置参数可以省略参数名。
        'count': 0,
        'result': '',
        'max_count': 300},
        config={'recursion_limit': 6 }   # 设置递归限制
        )
    """
    graph.invoke(
        input={...},        # 必填：初始状态
        config={...}        # 选填：运行时配置
        )
    其中recursion_limit:6 —— 递归/步骤限制。限制图的最大执行步数，防止死循环。默认通常是 25
    """
    print("=== 执行结果 ===")
    print(result)
except GraphRecursionError as e:
    print(f"GraphRecursionError递归错误: {e}")

"""
=== 开始执行工作流 ===
执行节点a，当前计数: 0
未满足终止条件，计数 1 < 300，返回b
执行节点b，当前计数: 1
执行节点a，当前计数: 1
未满足终止条件，计数 2 < 300，返回b
执行节点b，当前计数: 2
执行节点a，当前计数: 2
未满足终止条件，计数 3 < 300，返回b
执行节点b，当前计数: 3
GraphRecursionError递归错误: Recursion limit of 6 reached without hitting a stop condition. You can increase the limit by setting the `recursion_limit` config key.
For troubleshooting, visit: https://docs.langchain.com/oss/python/langgraph/errors/GRAPH_RECURSION_LIMIT
"""

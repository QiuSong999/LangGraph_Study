"""
上一章节发现乘法有个默认初始值为0，导致后续的计算都为0
在 Python 的 TypedDict 中，如果你不显式初始化，数字类型的默认值通常是 0 或 0.0。
问题所在：数学上，任何数乘以 0 都等于 0。如果直接用 current * update，只要初始值是 0，结果永远都是 0，乘法链条就断了。

对于不同操作，需要不同处理：
加法：恒等元是0.0，所以operator.add可以直接用（默认值初始值为0）
乘法：恒等元是1.0，需要特殊处理初始的0.0（需要默认值初始值为1）
自定义reducer是标准做法：复杂的业务逻辑都应该使用自定义reducer

这是LangGraph使用中的一个常见陷阱！建议在使用乘法、除法等非加法操作时，总是使用自定义reducer来处理初始值问题

    在执行初始阶段（我们定义的第一个node前），会默认调用一次reducer（后面自定义reducer案例中进行了打印验证），
    用默认值与invoke传递的值进行计算：
    此案例中，invoke中传递了一个默认值5.0，由于会默认调用一次reducer，
    执行的计算是： 0.0（float默认值） * 5.0(invoke传递的初始值) = 0.0
    导致后续乘法结果一直都是0

    初始默认值: factor = 0.0
    invoke传入: factor = 5.0
    reducer计算: 0.0 * 5.0 = 0.0
    然后才执行你的multiplier节点...
operator.mul作为 LangGraph 归约器的执行逻辑是：
最终值 = 初始值 * 增量值1 * 增量值2 * ...
归约器会迭代节点返回的增量值并依次相乘，若直接返回单个数值（非可迭代），
会被判定为「无增量」，最终按初始值 * 空处理，而乘法中「空累积」的默认结果是乘法单位元 0.0。

    解决方案： 使用自定义reducer
    """

import operator
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

### 1、 使用自定义reducer解决乘法问题:
def MyOperatorMul(current: float, update: float) -> float:
    """自定义乘法reducer，处理初始值为1.0"""
    # 如果是第一次调用，current会是默认值0.0
    if current == 0.0:
        # 对于乘法，恒等元应该是1.0或者 return 1.0 * update
        print(f"current:{current}")
        print(f"update:{update}")
        return 1.0 * update     #
    return current * update
"""
#调用
graph.invoke({"factor": 5.0})
#LangGraph 自动调用 Reducer
MyOperatorMul(
    current=0.0,   # State 中 factor 的默认值
    update=5.0     # invoke 传入的 {"factor": 5.0} 中的值
)
# 返回 5.0
"""

## 2、定义状态State
class MultiplyState(TypedDict):
    """系统默认，不要再用
    factor: Annotated[float, operator.mul]
             ↓                        """
    # 用自定义的
    factor: Annotated[float, MyOperatorMul]     #⭐MyOperatorMul为自定义reducer


## 3、定义节点Node(就是干活的函数)
def multiplier(state: MultiplyState) -> dict:
    return {"factor": 2.0}

## 4、定义一个总函数，包括了构建图graph、添加Node、Edge,编译图
def run_demo():
    print("使用自定义reducer解决乘法问题:")
    builder = StateGraph(MultiplyState)             #构建图

    builder.add_node("multiplier", multiplier)      #添加节点

    builder.add_edge(START, "multiplier")
    builder.add_edge("multiplier", END)

    graph = builder.compile()                       #编译图

    result = graph.invoke({"factor": 5.0})          #运行
    print(f"初始状态: {{'factor': 5.0}}")
    print(f"执行结果: {result}")  # 应该是 {'factor': 10.0}
    print(f"解释: 5.0 * 2.0 = 10.0\n")

if __name__ == "__main__":
    run_demo()

    """
    使用自定义reducer解决乘法问题:
    current:0.0
    update:5.0
    初始状态: {'factor': 5.0}
    执行结果: {'factor': 10.0}
    解释: 5.0 * 2.0 = 10.0
    """

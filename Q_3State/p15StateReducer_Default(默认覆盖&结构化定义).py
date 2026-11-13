'''
如果未明确指定reducer函数，则默认对该键的更新是覆盖行为。
LangGraph Reducer函数演示 - 默认Reducer（覆盖更新）

直接覆盖：
如果没有为状态字段指定 Reducer，默认会覆盖更新。
也就是说，后执行的节点返回的值会直接覆盖先执行节点的值，
即下一个节点的State数据是上一个节点的返回。
'''

from typing import List
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

### 1、定义State状态类
"""
默认Reducer（覆盖更新）
未指定合并策略，默认覆盖，上一个节点的返回是下一个节点的值
"""
class DefaultReducerState(TypedDict):
    foo: int
    bar: List[str]      #⭐字符串列表（没写 Annotated[]就是默认覆盖）

### 2、定义节点Node(就是干活的函数)
## 2.1节点1
def node_default_1(state: DefaultReducerState) -> DefaultReducerState:
    print("state[foo] =",state["foo"])      #等价于print(f"state[foo] = {state['foo']}")
    #输出state[foo] = 1
    """
    a="state[foo] ="
    b={"foo":1}
    print(a,b["foo"])           #print()一次打印多个，中间用,隔开。输出结果不换行，而是中间有个空格
    输出结果为：state[foo] = 1    #a是字符串，b是字典，b["foo"]表示根据键取值
    """

    print("state[bar] =",state["bar"])
    # 输出state[bar] = ["hi"]
    """
    为什么叫「默认覆盖型 Reducer」
        LangGraph 默认采用「字段级覆盖更新」，不是把整个状态字典替换，只修改你返回的字段，其余字段保留。
        针对同一个字段：新值直接覆盖旧值，不做拼接或者追加。
        节点返回 {键: 新值}，LangGraph 会增量合并：
        只更新返回中存在的 key，同 key 直接用新值覆盖旧值，状态里未被返回的 key 保持原值
    """

    # 写法1
    return {"foo": 22}
    """
    写法2 —— 返回完整状态字典对象
        state["foo"] = 22
        return state  # 返回完整字典
    """
# 经过节点1，全局State更新为：
#     {"foo": 22, "bar": ["hi"]}


## 2.2 节点2
def node_default_2(state: DefaultReducerState) -> dict:
    print()
    print("state[foo] =",state["foo"])       #输出 state[foo] = 22
    print("state[bar] =",state["bar"])       #输出 state[bar] = ['hi']
    return {"bar": ["bye1","bye2","bye3"]}

# 经过节点2，全局State更新为：
#     {"foo": 22, "bar": ["bye1","bye2","bye3"]}


### 3、定义一个总函数⭐⭐⭐(包括了构建图graph、添加Node、Edge、编译图、运行)
def main():
    print("-------默认Reducer（覆盖更新）演示:\n")
    builder = StateGraph(DefaultReducerState)   #⭐传入定义的State状态类

    builder.add_node("node1", node_default_1)
    builder.add_node("node2", node_default_2)

    builder.add_edge(START, "node1")
    builder.add_edge("node1", "node2")
    builder.add_edge("node2", END)

    graph = builder.compile()       #编译图（LangGraph 的"启动开关"）

    result = graph.invoke({"foo": 1, "bar": ["hi"]})   #运行
    # invoke()方法只接收状态字典作为核心参数

    print(f"执行结果: {result}\n")
    #输出
    #   执行结果: {'foo': 22, 'bar': ['bye1', 'bye2', 'bye3']}


if __name__ == "__main__":
    '''
    分步执行拆解
    
    进入 node1：接收 foo=1, bar=["hi"]   
    返回 {"foo": 22}
    合并后新状态：foo=22（被覆盖），bar=["hi"]（保留）
    
    进入 node2：接收 foo=22, bar=["hi"]  
    返回 {"bar": ["bye1","bye2","bye3"]}
    合并后最终状态：foo=22（保留），bar 被新列表覆盖
    '''
    main()




#data: Annotated[List[int], None]  #默认覆盖
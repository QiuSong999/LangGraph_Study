"""
图是一种由节点和边组成的用于描述节点之间关系的数据结构，分为无向图和有向图，
有向图是带有方向的图。LangGraph通过有向图定义AI工作流中的执行步骤和执行顺序，从而实现复杂、有状态、可循环的应用程序逻辑。
"""
'''
图的构建流程：
    1、定义状态
    2、初始化一个StateGraph实例。
    3、添加节点。
    4、定义边，将所有的节点连接起来。
    5、编译图。
    6、执行工作流。
'''

from typing import TypedDict
from langgraph.constants import START, END
from langgraph.graph import StateGraph

### 1. 定义状态机对象Obj
'''
TypedDict（推荐方式）: 
TypedDict是Python提供的一种类型提示工具，用于为字典（Dict）的键和值指定精确的类型信息。
状态类GraphStateObj继承TypedDict
'''
class GraphStateObj(TypedDict):
    process_data: dict
"""
process_data：这是字典中的一个键名。在 LangGraph 中，这代表状态里的一个具体数据槽位。
: dict：这是类型注解。它规定了 process_data 这个键对应的值，必须是一个字典类型。
如果这里写的是 str，那就意味着该值必须是字符串；如果是 int，则必须是整数。
"""

### 2. 定义节点， 统一使用 GraphStateObj类对象 做类型注解
#节点1
def input_node(state: GraphStateObj) -> GraphStateObj:
    print(f"input_node节点执行:  {state.get('process_data')}")
    #从当前状态字典中获取键名为 'process_data' 的值，（'process_data' 的值仍然是个字典键值对）
    """
    为什么要用 .get() 而不是 []？ 
    这是一个防御性编程的好习惯。如果 'process_data' 这个键还不存在（例如流程刚开始，状态是空的），使用 [] 会直接报错（KeyError），
    而 .get() 会安全地返回 None，保证程序不崩溃。
    python中根据键取值：
        字典名[]（中括号）：强硬派 —— 找不到报错；
        字典名.get()：温和派 —— 没找到：不报错，而是返回一个默认值。如果你没指定默认值，它就返回 None
    """

    new_data = state["process_data"].copy()   # 复制原有数据，而非直接覆盖（从 State 中取出 process_data 这个字典）
    #print(new_data.keys())
    new_data["k1"] = "input_value张三"        #给new_data新加键值对 "k1":"input_value张三"
    # LangGraph 默认采用「字段级覆盖更新」，不是把整个状态字典替换，只修改你返回的字段，其余字段保留。

    # 写法1(只返回修改过的)
    return {"process_data": new_data}

    # 写法2 返回完整状态字典对象
    #return state

# 节点2
def process_node(state: GraphStateObj) -> GraphStateObj:
    print(f"process_node节点执行:  {state.get('process_data')}")    #本节点干活之前，先把上一个节点返回值打印出来
    new_data = state["process_data"].copy()
    new_data["process"] = "process_value9527"       #新加的键值对
    return {"process_data": new_data}

#节点3
def output_node(state: GraphStateObj) -> GraphStateObj:
    print(f"output_node节点执行:  {state.get('process_data')}")
    # 直接透传当前状态
    return state

## 3. 初始化状态图
graph = StateGraph(GraphStateObj)

## 4. 添加节点
graph.add_node("input", input_node)
graph.add_node("process", process_node)
graph.add_node("output", output_node)

## 5. 定义边：执行顺序：START → input → process → output → END，线性执行。
graph.add_edge(START, "input")
graph.add_edge("input", "process")
graph.add_edge("process", "output")
graph.add_edge("output", END)

## 6. 编译图
app = graph.compile()

## 7. 执行工作流
init_data = {"process_data": {"name": "测试数据", "value": 111111}}     #要上传的字典（初始状态），invoke后先上传到节点1
result = app.invoke(init_data)
    # 调用 invoke，传入 init_date, LangGraph 内部：把 init_data 作为初始 State,从 START 出发，找到第一个节点 "input"……
print(f"\n最后的结果是:{result}")
"""
输出结果为：（每次累加进去）
    input_node节点执行:  {'name': '测试数据', 'value': 111111}
    process_node节点执行:  {'name': '测试数据', 'value': 111111, 'k1': 'input_value张三'}
    output_node节点执行:  {'name': '测试数据', 'value': 111111, 'k1': 'input_value张三', 'process': 'process_value9527'}

最后的结果是:{'process_data': {'name': '测试数据', 'value': 111111, 'k1': 'input_value张三', 'process': 'process_value9527'}}
"""
print("-"*35)

# ASCII 可视化
print("\n===== 图结构 ASCII =====")
print(app.get_graph().print_ascii())
print("*"*35)

# Mermaid 源码
print("\n===== Mermaid 代码 =====")
print(app.get_graph().draw_mermaid())
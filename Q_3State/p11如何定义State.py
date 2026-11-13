"""定义State"""
"""
把 TypedDict 比作数据库表的表头（Schema），是理解它最快、最直观的方式。
1. 字段名 = 列名
    数据库表头：定义了这张表有哪些列，比如 user_id, name, age。
    TypedDict：定义了状态对象里有哪些“键”，比如 user_input, response, count。
    作用：它们都规定了数据的结构。如果你试图往表里插入一列不存在的 gender，或者在代码里访问一个没定义的 state['gender']，都会报错或不符合规范。
2. 数据类型 = 数据类型约束
    数据库表头：每一列都有类型，比如 INT（整数）、VARCHAR（字符串）。你不能把“张三”存进 age 这一列。
    TypedDict在写代码时（编译期或IDE提示阶段）就帮你检查数据格式，防止你把字符串当成数字去加减。

表头(Schema)：只是定义规则。你现在的代码 class BasicState... 仅仅是在画这张表的“设计图”。它本身不存数据，就像表头本身不存“张三”这个名字一样。
    行数据 (Instance/Row)才是实际内容。当你的 LangGraph 跑起来时，内存里那个不断变化的 state 变量，才相当于表里的“某一行数据”。

进阶理解：LangGraph 的 State 更像“单行记录的演变”
    在数据库中，表通常有很多行（很多用户的数据）。但在 LangGraph 的这一次对话流程中，BasicState 通常只对应当前这一个任务/对话的“唯一一行数据”。
    随着节点一个个执行，这“一行数据”里的值在不断被修改、更新

即：class BasicState(TypedDict) = 建表语句（定义表头、列名、类型），运行时的 state 变量 = 表里正在被编辑的那一行数据。
    除了TypedDict，还有BaseModel等其他，但是很少用。
"""

from typing import TypedDict
from langgraph.graph import StateGraph, START, END

### 1.定义状态State
#⭐基本上所有的状态都写继承于TypedDict⭐
class BasicState(TypedDict):    #相当于每一张数据表的表头
    """基本的 State定义"""
    user_input: str
    response: str
    count: int
    process_data: dict

"""没定义节点Node因为本章主要是为了演示定义State"""

### 2.创建状态图，并指定状态结构
builder = StateGraph(BasicState)

### 3. 添加起始到结束的边（无中间节点）
builder.add_edge(START, END)

### 4.编译生成计算图
graph = builder.compile()


### 4、运行
initial_state = {       #要输入的初始状态，单独成段
    "user_input": "a",
    "response": "resp",
    "count": 25,
    "process_data": {"k1": "v1"}    # process_data本身是dict类型，需嵌套
}   #★本章节未定义节点，所以最后输出的结果就是传进去的结果

# invoke()方法只接收状态字典作为核心参数
# invoke() 仅接收 1 个核心位置参数（状态字典），可选 1 个配置参数，切勿传入多个独立参数。
# 嵌套可以，如上面的initial_state就是字典里面嵌套了个字典
result = graph.invoke(initial_state)

# 打印结果验证
print("执行结果：", result)

"""
输出如下：
    执行结果： 
    {'user_input': 'a', 
    'response': 'resp', 
    'count': 25, 
    'process_data': {'k1': 'v1'}}
"""

"""
节点缓存策略
这段代码实现了 LangGraph 的节点缓存：第一次执行节点耗时 3 秒，8 秒内再次执行相同输入直接返回缓存结果，8 秒后缓存过期重新计算。
"""
"""
在 LangGraph 这类图执行框架中，节点缓存通常指的是计算结果缓存（Computational Caching）。

    作用：当图中的某个节点执行了耗时或昂贵的计算（如调用外部大模型、复杂数据处理）后，将结果缓存起来。
    如果图再次运行且输入条件未变，就可以直接复用缓存结果，跳过该节点的重复执行。
    
    优势：极大提升图的执行效率，节省 Token 消耗和 API 调用成本。

实现方式：LangGraph 官方提供了 CachePolicy 机制，允许开发者为特定节点配置缓存策略，框架会根据节点的输入状态（State）
自动生成缓存键（Cache Key）并管理生命周期。（即在添加节点的函数.add_node()中，多上传一个参数）
"""
"""
LangGraph支持基于节点输入对任务/节点进行缓存。使用缓存的方法如下:
★★编译图(或指定入口点)时指定缓存。
为节点指定缓存策略。每个缓存策略支持:
    key_func用于根据节点的输入生成缓存键，默认情况下是使用pickle对输入进行hash运算的结果。
    ttl，即缓存的生存时间(以秒为单位)。如果未指定，缓存将永不过期。
    
特性：
    缓存键与命中:当一个节点开始执行时，系统会使用其配置的key_func根据当前节点的输入数据生成一个唯一的键。
    LangGraph|会检查缓存中是否存在这个键。如果存在(缓存命中)，则直接返回之前存储的结果，跳过该节点的实际执行。
    如果不存在(缓存未命中)，则正常执行节点函数，并将结果与缓存键关联后存入缓存。

    缓存有效期:ttl参数能控制缓存的有效期。例如，对于依赖实时数据的天气查询节点，可以设置较短的t(如60秒),
    而对于处理静态信息或变化不频繁数据的节点，则可以设置较长的t甚至不设置(None)，让缓存永久有效，直到手动清除
    ttl即time to leave
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
⭐⭐⭐
节点缓存的实现分两步：
    1、添加节点的时候add_node()里面传 cache_policy 来控制单个节点是否使用缓存 → 告诉这个节点“我要缓存”
    2、编译图的时候builder.compile()里面上传cache → 提供缓存存储位置
"""

import time
from typing_extensions import TypedDict
from langgraph.graph import StateGraph
from langgraph.cache.memory import InMemoryCache
from langgraph.types import CachePolicy

### 1、定义状态类，也就是你的业务实体entity
class State(TypedDict):
    x: int
    result: int

### 2、 创建图
builder = StateGraph(State)

### 3、 定义节点：模拟耗时计算（sleep3秒）
def expensive_node(state: State) -> dict[str, int]:
    time.sleep(3)       #模拟一个耗时的操作
    return {"result": state["x"] * 2}       # *2计算

##~~~~~~~~~~~~~~~~~~~~~~~~~ 4、添加节点：每个节点都可以独立配置自己的缓存策略，互不影响~~~~~~~~~~~~~~~~~~~~~~~~~
builder.add_node(node="expensive_node",action=expensive_node,       #之前只传名字和节点函数名，就是这两个参数
    # 不用传key_fn，底层自动用默认逻辑
    cache_policy=CachePolicy(ttl=8)     #⭐缓存策略,ttl是缓存的生存时间（秒为单位），如果未指定则缓存永不过期
)
"""
cache_policy：这是 add_node() 方法的一个参数，专门用来配置该节点的缓存策略。
    CachePolicy：是LangGraph 提供的一个类，用于定义缓存的具体行为。
    ttl=8：TTL 是 Time To Live 的缩写（存活时间)
"""

## 设置入口和出口(换个写法，和START与END同效果)
builder.set_entry_point("expensive_node")       #相当于 builder.add_edge(START, "expensive_node")
builder.set_finish_point("expensive_node")

### 5、 编译图，指定内存缓存~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
graph = builder.compile(cache=InMemoryCache())    #⭐InMemoryCache 字面意思就是内存缓存
    #⭐之前不上传参数，无缓存；现在传了参数，图就有了“记忆”，可以把运行状态（State）保存下来，快速复用
"""
InMemoryCache 字面意思就是内存缓存。传入它意味着：
1、缓存图的历史状态（State）：每当图执行完一步（比如跑完一个节点），LangGraph 就会把当前的 State 
    及其对应的“执行时间点（Thread ID / Checkpoint ID）”存入内存。
2、支持断点续跑/时间旅行：由于保存了历史状态，你可以让图退回到之前的某个步骤，或者从某个中断的地方继续执行，而不需要重新从头开始跑。
3、开启“记忆”：你的图现在可以处理多轮对话或者需要依赖上下文的任务了（这对于构建聊天机器人等长流程应用至关重要）。

注意：InMemoryCache()意味着它存在 RAM（内存）里：速度极快，但是程序一旦关闭或重启，缓存就会全部丢失。
    如果你的应用需要长期保存（比如跨天、跨进程）， 绝对不能用 InMemoryCache。你需要使用基于数据库的持久化缓存，例如
        from langgraph.checkpoint.sqlite import SqliteSaver         #导入依赖
        app = builder.compile(checkpointer=SqliteSaver.from_conn_string("checkpoints.sqlite"))  #使用 SQLite 数据库保存状态
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
假设前面有两个节点，一个节点上传了缓存策略add_node(cache_policy=)，
另一个节点没有上传缓存策略add_node()
则传了 cache_policy 的节点会缓存，没传的节点不缓存。两者互不影响。
⭐只要前面有节点设置了缓存策略，编译图时.compile(cache=),这个cache参数一定要传
"""


# 第一次执行：耗时3秒（无缓存）
print("第一次执行（无缓存，耗时3秒）：")
print(graph.invoke({"x": 5}))
# 第一次执行（无缓存，耗时3秒）：
# {'x': 5, 'result': 10}
print("①"*25)

# 第二次执行：瞬间返回（利用缓存，8秒内有效）
print("第二次运行利用缓存并快速返回：")
print(graph.invoke({"x": 5}))     #上面第一次执行出结果过后，第二次执行8秒内会立马出现结果
# 第二次运行利用缓存并快速返回：
# {'x': 5, 'result': 10}
print("②"*25)

# 可选：测试8秒后缓存过期（取消注释查看）
print("\n等待8秒，缓存过期...")
time.sleep(8)       #模拟超过8秒的情况
print("8秒后第三次执行（重新计算，耗时3秒）：")
print(graph.invoke({"x": 5}))

"""
节点Node的优化策略：
    高频、小数据量的重要节点必加缓存，且配置缓存失效时间
"""
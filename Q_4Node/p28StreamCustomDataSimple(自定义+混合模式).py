"""自定义混合输出"""
'''
要从LangGraph节点或工具内部发送自定义用户定义数据，请遵循以下步骤：
⭐⭐⭐
	1、节点内部：使用 get_stream_writer() 拿工具，用 writer({...}) 发数据
	2、外部接收：graph.stream(..., stream_mode=["custom"]) 在流中获取自定义数据。
你可以组合多种模式（例如["updates", "custom"]），但至少有一种模式必须是"custom"。

LangGraph 自定义数据流式传输演示（不是updates也不是values，而是采用自定义的模式）
展示如何从节点内部发送自定义用户定义数据
'''
"""
自定义流式输出，可以看到不在状态State里面定义的变量的输出过程；即可以看到Note节点定义的变量流式输出
方法：
    在节点函数里调用 get_stream_writer() 拿到 writer 实例，
    直接调用 writer({...}) 传入任意自定义数据块（同样在节点函数中）
    接收端（输出的时候）把 stream_mode 设为 "custom"，就能实时捕获这些数据。
    
get_stream_writer() 的特点：
特点	                说明
只在节点函数中用	只能在 add_node 绑定的函数里调用
每个节点独立	    每个节点都有自己的 writer
发送任意数据	    可以发字典、列表、字符串等
实时送达	        发送后立即被 stream() 捕获
"""

from typing import TypedDict
from langgraph.config import get_stream_writer
from langgraph.graph import StateGraph, START,END

### 1、定义状态state
class State(TypedDict):
    query: str
    answer: str

#### 2、 定义节点函数，在节点函数里调用 get_stream_writer() 拿到 writer 实例
def node(state: State):
    # 节点函数里调用 get_stream_writer() 拿到 writer 实例
    writer = get_stream_writer()                    #⭐自定义输出模式必须要用这个函数
    #LangGraph 的函数，返回一个发送工具

    writer({"custom_key": "欢迎来到尚硅谷线学习，☺"})   #直接调用 writer({...}) 传入任意自定义数据块
    #           ↑               ⭐⭐⭐核心作用：让用户不用干等，能看到实时反馈。
    #  这个键名是你自己起的，不是固定的，
        #⭐在节点执行过程中，实时向外推送一条自定义消息“欢迎来到尚硅谷线学习，☺”，而不是等节点跑完才返回结果
    return {"answer": "some data end"}
"""
writer = get_stream_writer() 是拿一个“发送消息的工具”，让你能在节点执行过程中往外发数据
writer({"custom_key": "欢迎来到尚硅谷线学习，☺"})      #用上面“发送消息的工具”发出一条消息
~~~~~~~~~~~
有什么用？
    没有它，节点只能最后通过 return 返回数据：
    def node(state):
        # 中间过程无法通知外界
        time.sleep(5)   # 用户干等5秒
        return {"result": "完成"}     # 只有最后才能返回
        
    有了它，节点可以随时发送数据：
    def node(state):
        writer = get_stream_writer()
        writer({"status": "开始处理..."})   # 立即发送
        time.sleep(2)
        writer({"status": "处理中 50%"})    # 发送进度
        time.sleep(2)
        writer({"status": "完成！"})        # 发送完成
        return {"result": "完成"}           # 最后返回
"""

### 3、~~~~~~~⭐一体式建Graph（创建图、添加节点，连接成边，演绎图）~~~~~~~
graph = (
    StateGraph(State)
    .add_node(node)
    .add_edge(START, "node")
    .add_edge("node",END)
    .compile()
)

### 4、输出
# Set stream_mode="custom" to receive the custom data in the stream
for chunk in graph.stream({"query": "example"}, stream_mode=["custom"]):    #流式输出，自定义模式为custom
    print(chunk)
"""
输出结果为：('custom', {'custom_key': '欢迎来到尚硅谷线学习，☺'})
因为是自定义模式为custom，所以节点函数的return的未输出
只输出writer({"custom_key": "欢迎来到尚硅谷线学习，☺"})中的{"custom_key": "欢迎来到尚硅谷线学习，☺"}，并给其加上标签
即('custom', {'custom_key': '欢迎来到尚硅谷线学习，☺'})，
'custom'是 LangGraph 在“混合流式模式”下，为了让你区分数据来源，强制给数据贴上的“标签”,代表这是“自定义流式输出”模式的数据
"""
print("①"*20)


for chunk in graph.stream({"query": "example"}, stream_mode=["updates", "custom"]):     #增量+自定义
    print(chunk)
#有了列表 ["updates", "custom"]，图引擎知道你在“混收”。为了避免你分不清收到的数据属于哪个模式，
# 引擎会强制将它们包装成 (模式名, 数据内容) 的元组格式。
"""
自定义模式 + 增量模式，输出结果如下：（同样会增加标签）
    ('custom', {'custom_key': '欢迎来到尚硅谷线学习，☺'})  #自定义的输出
    ('updates', {'node': {'answer': 'some data end'}})  #增量输出，其中updates代表是增量，node代表该节点的输出
"""
print("②"*20)


for chunk in graph.stream({"query": "example"}, stream_mode=["values", "custom"]):       #全量+自定义
    print(chunk)
"""
输出如下：
    ('values', {'query': 'example'})
    ('custom', {'custom_key': '欢迎来到尚硅谷线学习，☺'})
    ('values', {'query': 'example', 'answer': 'some data end'})
"""

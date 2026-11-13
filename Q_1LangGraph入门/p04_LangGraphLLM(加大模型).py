"""
LangGraph 简单案例HelloWorld：
构建一个最小的有向图，流程是：START → 模型节点 → END

LangGraph的灵魂：State(状态) + Nodes(节点) + Edges(边) + Graph(图)
"""

""" 在定义节点之前构建大模型。⭐关键点：把调用大模型的代码写在节点函数中 """

import uuid
from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
import os
from langchain.chat_models import init_chat_model

# 这段代码实现了一个最简单的 AI 对话机器人——输入问题，大模型回答，并把对话记录下来
## ========== 1. 定义状态（State） ==========
# 存储对话消息
class AtguiguState(TypedDict):                      #TypedDict固定写这个
    messages: Annotated[List, add_messages]         #详细见p16
    # messages 是一个消息列表， Annotated + add_messages 表示支持自动追加消息
"""
Annotated 是 Python 3.9+ 的类型提示工具，用于给类型附加额外信息（元数据），而不改变类型本身
它的作用：它像一个“快递包裹”，把“类型”和“额外说明”打包在一起。在这里，它是为了给 List 这个类型附加一个“合并规则”（也就是 add_messages）。

# 基本语法
    Annotated[类型, 规则1]
写法	                                     是否可行	        说明
asspr: Annotated[List, add_messages]	✅ 可行	    使用 LangGraph 内置的 add_messages
asspr: Annotated[List, add_asspr]	    ✅ 可行	    使用你自己定义的 add_asspr 函数
"""

## ========== 2. 定义大模型 ==========
llm = init_chat_model(
        model="qwen-plus",
        model_provider="openai",
        api_key=os.getenv("aliQwen-api"),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )



## ========== 3. 定义节点函数 （在其中调用大模型）==========
# 节点：调用大模型，并把回复加入到 state["messages"] 里
def model_node(state: AtguiguState):
    reply = llm.invoke(state["messages"])   # 输入历史消息，调用大模型，reply是AIMessage对象
    # AtguiguState → 规定数据应该长什么样（可以理解成一张数据结构说明书/模板）；
    # state → 真正的数据。所以是state["messages"]
    return {"messages": [reply]}            # 返回新消息，自动加到 state
    # 此时的状态为：{"messages": [AIMessage对象]}



## ========== 4. 构建图结构 ==========
graph = StateGraph(AtguiguState)            # 创建图，用 AtguiguState （之前定义的state类名）作为状态结构

## ========== 5. 添加节点 ==========
graph.add_node("modeling", model_node)         # 添加节点，节点名叫 "model"，执行 model_node 函数

### ========== 6. 添加边 ==========
graph.add_edge(START, "modeling")      # 从入口 → 直接到 "modeling" 节点
graph.add_edge("modeling", END)       #  "modeling"节点执行完 → 结束
# 打印图的边和节点信息
print(graph.edges)
"""
输出结果：
    {('__start__', 'modeling'), ('modeling', '__end__')}
"""
print("-"*35)

print(graph.nodes)
"""
输出：
{'modeling': StateNodeSpec(runnable=modeling(tags=None, recurse=True, explode_args=False, func_accepts={}), 
metadata=None, input_schema=<class '__main__.AtguiguState'>, retry_policy=None, cache_policy=None, 
is_error_handler=False, error_handler_node=None, ends=(), defer=False, timeout=None, trace_policy=None)}
"""
print("①"*35)

# ========== 7. 编译图将图编译为可执行程序并启动==========
app = graph.compile()

# ========== 8. 运行 ==========
result = app.invoke({"messages": "请用一句话解释什么是 LangGraph。"})
#⭐⭐经过状态类定义 messages: Annotated[List, add_messages]，其中的“add_messages”会把改输入包装成HumanMessage对象
#result = app.invoke({"messages": [HumanMessage(content="请用一句话解释什么是 LangGraph。")]}) 与上等价
print(result)
"""
⭐
输出的结构如下：
    ｛ 'messages': [
                    HumanMessage(content='请用一句话解释什么是 LangGraph。', additional_kwargs={}, ...),
                    AIMessage(content='LangGraph 是一个基于图的框架...', additional_kwargs={...}, ...)
                  ]
        ｝
"""
print("②"*25)

# 打印模型的最后一条回复
print("模型回答：", result["messages"][-1].content)  #即打印上面的AIMessage对象的content部分
"""
运行后实际的输出结果为：
    模型回答： LangGraph 是一个基于图（Graph）的框架，用于构建具有状态、记忆和循环逻辑的复杂 AI 代理（Agent）工作流，
    它扩展自 LangChain，通过节点（Nodes）和边（Edges）显式建模状态流转与条件控制，支持异步、持久化和多轮对话等高级代理行为。
"""
print("③"*25)

# 这段代码实现了一个最简单的 AI 对话机器人——输入问题，大模型回答，并把对话记录下来

# =========================
#1. 打印图的ascii可视化结构
print(app.get_graph().print_ascii())    #⭐编译图.get_graph().print_ascii()
"""输出为：
+-----------+  
| __start__ |  
+-----------+  
      *        
      *        
      *        
+----------+   
| modeling |   
+----------+   
      *        
      *        
      *        
 +---------+   
 | __end__ |   
 +---------+   
None
"""
print("④"*50)

#2. 打印图的Mermaid代码可视化结构并通过https://www.processon.com/mermaid编辑器查看
print(app.get_graph().draw_mermaid())   #⭐get_graph().draw_mermaid()
"""输出为：
---
config:
  flowchart:
    curve: linear
---
graph TD;
	__start__([<p>__start__</p>]):::first
	modeling(modeling)
	__end__([<p>__end__</p>]):::last
	__start__ --> modeling;
	modeling --> __end__;
	classDef default fill:#f2f0ff,line-height:1.2
	classDef first fill-opacity:0
	classDef last fill:#bfb6fc
"""
print("⑤"*50)

#3. 生成 PNG并写入文件
png_bytes = app.get_graph().draw_mermaid_png()  #⭐.get_graph().draw_mermaid_png()
output_path = "langgraph" + str(uuid.uuid4())[:8] + ".png"
with open(output_path, "wb") as f:
    f.write(png_bytes)
print(f"图片已生成：{output_path}")   #图片生成：langgraph2d7fd3b3.png



from typing import TypedDict, List, Annotated   #
from langgraph.graph import StateGraph, START, END, add_messages
from langchain_core.messages import HumanMessage, AIMessage
"""⭐⭐⭐实现方式：在定义状态时，给字典名限制的时候设置Annotated[]"""

### 1、定义State状态类
"""add_messages Reducer（消息列表专用）"""
class AddMessagesState(TypedDict):
    """
    引入的 Annotated 类型，它允许给类型添加额外的元数据。
    messages: Annotated[List, add_messages]
    表示:
    - messages 我的状态里只有一个字段叫 messages，类型是是 List列表类型,
    - add_messages  这里的 add_messages 是一个函数，用于修改 messages 列表
                    每当节点返回对 messages 的“局部更新”时，
                    请用 add_messages 规约器把它合并到旧列表上（追加，而不是覆盖）
    总结：
    节点永远只 return 增量字典，不用手动把旧列表读出来再拼接。
    add_messages 在后台帮你完成“追加”动作；如果换成默认规则，旧消息会被整份替换掉
    """
    messages: Annotated[List, add_messages]
    #⭐“add_messages”会把改后面invoke()输入的字符串包装成HumanMessage对象
    """
    Annotated[类型, 标签] 就是给字段贴个标签，告诉框架（如 LangGraph）怎么处理它。
    add_messages 是 LangGraph 官方提供的固定函数名，专门用于处理对话消息列表的合并。故后续invoke()里面也应该上传message的字典
    ⭐⭐其中的“add_messages”会把改后面invoke()输入的字符串包装成HumanMessage对象
    列表消息场景 → 必须 Annotated[List, add_messages] 安全追加
    """


### 2、定义节点Node(就是干活的函数)
def chat_node_1(state: AddMessagesState) -> dict:
    return {"messages": [AIMessage(content="Hello from node 1")]}

def chat_node_2(state: AddMessagesState) -> dict:
    return {"messages": [AIMessage(content="Hello from node 2")]}


### 3、定义一个总函数，包括了构建图graph、添加Node、Edge、编译图、运行
def run_demo():
    print("add_messages Reducer（消息列表专用）演示:\n")
    builder = StateGraph(AddMessagesState)      #构建图
    # add(node + edge)
    builder.add_node("chat1", chat_node_1)      #添加节点
    builder.add_node("chat2", chat_node_2)

    builder.add_edge(START, "chat1")    #点连线添加边
    builder.add_edge(START, "chat2")    # 两个节点并行执行
    builder.add_edge("chat1", END)
    builder.add_edge("chat2", END)


    graph = builder.compile()                   #编译图compile

    ## 运行
    # 初始消息使用标准消息对象
    init_messages = [HumanMessage(content="Hi there!")]
    result = graph.invoke({"messages": init_messages})
    # result = graph.invoke({"message":"Hi there!")]}) 与上等价
    # ⭐⭐经过状态类定义 messages: Annotated[List, add_messages]，其中的“add_messages”会把输入的内容包装成HumanMessage对象
    """
    初始State为：{"messages": [HumanMessage(content="Hi there!")]}
    经过节点1处理后，State为
       {
       "messages": [
                    HumanMessage(content="Hi there!",additional_kwargs={}, response_metadata={},id='5……),
                    AIMessage(content="Hello from node 1",additional_kwargs={}, response_metadata={}, id='b……,tool_calls=[], invalid_tool_calls=[])
                    ]
       }
    经过节点2处理后，State为
       {
       'messages': [
                     HumanMessage(content='Hi there!', additional_kwargs={}, response_metadata={}, id='5045994e-bc8b-48d4-befa-2a7829b583a9'), 
                     AIMessage(content='Hello from node 1', additional_kwargs={}, response_metadata={}, id='b2721608-f55a-4a3c-a276-431d066aef4e', tool_calls=[], invalid_tool_calls=[]), 
                     AIMessage(content='Hello from node 2', additional_kwargs={}, response_metadata={}, id='93d0a0c0-08af-4bf6-9d2e-306cf4d3f609', tool_calls=[], invalid_tool_calls=[])
                     ]
       }
                ##每个列表都是一个类，可以用.content属性来取文本内容
    """


    ## 格式化输出，只展示核心内容，隐藏多余元数据
    print("执行结果:")
    for msg in result["messages"]:
        role = "user" if isinstance(msg, HumanMessage) else "assistant"
        """
        isinstance()  是 Python 的内置函数，检查一个对象是否属于某个类型（或某几个类型之一）
        返回值为True 或 False，例如：
            语法 isinstance(要检查的对象, 类型)             #返回True 或 False
                isinstance(5, int)                      #检查数字是否是 int 类型，输出： True
                isinstance([1, 2, 3], list)             #检查列表是否是 list 类型，输出 True
        """

        print(f"('{role}', '{msg.content}')")
        """
        执行的最终结果:
            ('user', 'Hi there!')
            ('assistant', 'Hello from node 1')
            ('assistant', 'Hello from node 2')
        """

    print("-" * 30)

    ## 打印图的ascii可视化结构
    print(graph.get_graph().print_ascii())

"""
       +-----------+         
       | __start__ |         
       +-----------+         
         *        *          
       **          **        
      *              *       
+-------+         +-------+  
| chat1 |         | chat2 |  
+-------+         +-------+  
         *        *          
          **    **           
            *  *             
        +---------+          
        | __end__ |          
        +---------+          
None

#发现最后一行有个None,原因非常简单因为 print_ascii() 自己已经完成了打印工作，
#不需要再用 print() 包裹它。这样控制台就只会显示 ASCII 图形，而不会多出一个 None 

拆解一下代码执行过程：
    执行内层函数： graph.get_graph().print_ascii()
        这一步的作用是直接把图形以 ASCII 字符的形式“打印”到控制台（即你看到的那个由 *, +, |, _ 组成的图形）。
    因为这一步的作用是“打印”，所以它执行完后，函数默认返回 None（在 Python 中，没有 return 语句的函数会隐式返回 None）。
    
    执行外层函数： print( ... )
    print() 函数接收到了内层函数返回的 None，然后试图把它打印出来。
    所以最后一行就会出现 None。
"""

### 4、运行这个系统
if __name__ == "__main__":
    run_demo()
    #一个节点绑定一个模型，这样就可以输出两个模型的结果，该案例没有调用模型
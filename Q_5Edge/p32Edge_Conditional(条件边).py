"""
条件边的执行逻辑：通过定义一个函数，从状态中取值 判断
"""
"""
LangGraph 条件边
    分支流程控制语句分支路由（Router → Weather / Chat）
    使用langgraph构建了一个状态图，根据输入数值的“奇偶性”执行不同节点。
        check_x接收并传递状态，
        is_even判断奇偶，
        handle_even和handle_odd分别处理偶数和奇数情况，最终输出结果。
~~~~~~~~~~~~~~~~~~~~~~~
add_edge()普通边：固定线路
add_conditional_edges()：根据条件选择路线
"""

"""
创建检查节点函数、条件判断函数
⭐⭐⭐
条件边的实现方式：
    用 add_conditional_edges() 方法，传入起点节点、路由函数、路径映射表。
add_conditional_edges(
        source,           # 必填，源头节点：从哪个节点触发判断
        path,             # 必填，路由函数：接收当前 State 并返回一个标记（如字符串）的函数
        path_map=None,    # 选填，路径映射表（字典或列表），默认为None：将路由函数的返回值映射到真实的下一个节点名称。
        then=None         # 选填，汇合节点名，默认为None
    )
"""

from typing import Optional
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from loguru import logger
from pydantic import BaseModel

### 1.定义状态State
class MyState(BaseModel):
    """
    定义状态模型，用于在图节点之间传递数据
    Attributes:
        x (int): 输入的整数
        result (Optional[str]): 处理结果，可为"even"或"odd"
    """
    x: int
    result: Optional[str] = None    #Optional表示值不固定，可能有多种存在

    """
    result—— 类型注解;
    Optional[str] —— 可选类型(这个字段的值可以是字符串，也可以是 None),Optional 是 Python 的 typing 模块中提供的一个泛型别名
    该行代码整体意思是：定义了一个名为 result 的字段，它的数据类型是字符串 (str)，但它也可以是空值 (None)，并且默认初始值为 None
    """

### 2.创建节点函数（包括查节点、判断函数、每种情况执行的处理节点函数）~~~~~~~~~~~~~~~~

## 2.1 创建检查输入状态的节点函数（检查节点）
def check_x(state: MyState) -> MyState:
    """
    检查输入状态的节点函数
    Args:
        state (MyState): 包含输入数据的状态对象
    Returns:
        MyState: 返回原始状态对象，未做修改
    """
    logger.info(f"【check_x】 Received state: {state}")   #接收 State，打印一下，原样返回
    return state
# ⭐⭐条件边必须从某个节点出发，本案例check_x 就是那个“出发的节点”,但 START 或业务节点也可以做起点。

## 2.2 判断状态中x值是否为偶数的条件函数 （条件判断/“路由函数”）（非节点）
def is_even(state: MyState) -> bool:
    """
    判断状态中x值是否为偶数的条件函数
    Args:
        state (MyState): 包含待判断数值的状态对象
    Returns:
        bool: 如果x是偶数返回True，否则返回False
    """
    return state.x % 2 == 0     # 判断x是不是偶数，是就返回 True，不是就返回 False
    """
    “路由”：就是“路标”和“指路牌”。它的核心工作只有一件：收到一个请求/指令后，决定接下来该把数据送到哪里去处理。
    
    路由函数: 基于“当前状态/判断结果”指路的函数。
    场景	            输入条件（依据什么指路？）	输出目的地（送去哪里？）
    FastAPI路由	    HTTP 请求的网址URL	    对应的后端处理函数
    Graph路由	    工作流当前的状态/AI判断  	图结构中的下一个节点 (Node)
    """

## 2.3 不同的节点函数
# 2.3.1 处理偶数情况的节点函数（偶数处理节点）
# 当 is_even 返回 True 时执行
def handle_even(state: MyState) -> MyState:
    """
    处理偶数情况的节点函数
    Args:
        state (MyState): 包含偶数输入的状态对象
    Returns:
        MyState: 返回更新后的状态对象，result设置为"even"
    """
    logger.info("[handle_even] x 是偶数")
    return MyState(x=state.x, result="even")
"""
return返回的是MyState(...)： 是创建一个 Pydantic 模型实例，等价于返回一个字典。为什么要这样，而不是像之前返回字典？
因为定义状态State时用的是 Pydantic 的BaseModel，不是TypedDict ——（class MyState(BaseModel)），实际效果一样

State 的类型不同，习惯用法也不同。
    State 类型	   推荐返回写法
    TypedDict	字典 {"key": value}
    BaseModel	对象 MyState(key=value)
    
场景	        用的 State 类型	            返回写法
之前      HelloState	TypedDict	return {"greeting": "..."}
现在      MyState	BaseModel	return MyState(x=..., result=...)
"""

#2.3.2处理奇数情况的节点函数（奇数处理节点）
def handle_odd(state: MyState) -> MyState:
    """
    处理奇数情况的节点函数
    Args:
        state (MyState): 包含奇数输入的状态对象
    Returns:
        MyState: 返回更新后的状态对象，result设置为"odd"
    """
    logger.info("[handle_odd] x 是奇数")
    return MyState(x=state.x, result="odd")
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

### 3.构建图
builder = StateGraph(MyState)

### 4. 添加节点
# #⭐⭐⭐负责“判断”的函数（ is_even）不需要作为独立的节点添加到图中
builder.add_node("check_x", check_x)            #检查节点要添加到图上
builder.add_node("handle_even", handle_even)    #括号内的两个参数：前面是器的节点名，后面是节点函数
builder.add_node("handle_odd", handle_odd)

### 5.添加边（添加普通边和条件边的顺序不影响最终结果）
## 5.1 添加条件边，根据is_even函数的返回值决定流向哪个节点~~~~~~~~~~~~~~~~~~~~~~~~~~~~
builder.add_conditional_edges("check_x", is_even, {     #⭐三个参数分别为：起始节点、判断函数、映射表
    True: "handle_even",    #is_even判断为True,就走处理偶数情况的节点函数     #True和False是按照判断节点的返回值来填写的,不是固定死的
    False: "handle_odd"     #判断为False就走处理奇数情况的节点函数
})
"""
.add_conditional_edges() —— 根据当前 State（状态）的内容，动态决定下一步该走哪个节点
    格式：
        add_conditional_edges(
            source,           #必填，起点节点的名称。告诉图，从哪个节点出发进行条件判断
            path,             #必填路由函数或路由逻辑。这是条件路由的核心，它决定了图怎么走。
                                #传入一个函数，该函数接收当前的 state 作为输入，返回一个字符串（目标节点名）或一个可哈希的值（用于匹配路径映射）。
            path_map=None,    #选填，路径映射表
            *, 
            condition=None
        )
"""

## 5.2 添加普通边Edge
# 添加起始边，从START节点流向check_x节点
builder.add_edge(START, "check_x")


# 添加结束边，从处理节点流向END节点
builder.add_edge("handle_even", END)
builder.add_edge("handle_odd", END)

### 6. 编译图结构
graph = builder.compile()

### 7. 打印图的可视化结构
print(graph.get_graph().print_ascii())
#输出结果如下
"""
输出：
              +-----------+               
              | __start__ |               
              +-----------+               
                    *                     
                    *                     
                    *                     
               +---------+                
               | check_x |                
               +---------+                
             ...          ..              
            .               ..            
          ..                  ..          
+-------------+           +------------+  
| handle_even |           | handle_odd |  
+-------------+           +------------+  
             ***          **              
                *       **                
                 **   **                  
               +---------+                
               | __end__ |                
               +---------+                
None
"""
logger.info("①"*20)


### 8.测试用例：输入偶数4
result1 = graph.invoke(MyState(x=4))        #初始状态输入的是：{"x": 4, "result": None}
#⭐.invoke()里面可以上传字典，也可上传状态定义的对象
"""
⭐⭐
LangGraph 中，graph.invoke() 的输入确实既可以是字典（dict），也可以是 Pydantic 模型实例。
你之所以看到传入 MyState(x=4) 也能正常运行，是因为你在定义状态时使用了 Pydantic 的 BaseModel（即class MyState(BaseModel):）
"""
logger.info(result1)    #输出：{'x': 4, 'result': 'even'}

logger.info("②"*20)

### 9. 测试用例：输入奇数3
result2 = graph.invoke(MyState(x=3))
logger.info(type(result2))      #输出：<class 'dict'>
logger.info(result2)            #输出：{'x': 3, 'result': 'odd'}

"""
检查节点不是必须的

场景	                   需要检查节点吗？	       原因
条件边从 START 出发	    ❌ 不需要	    START 可以直接做起点
条件边从某个业务节点出发	❌ 不需要	    业务节点本身就能做起点
想在判断前先做点事	        ✅ 可以加	    比如打印、校验、预处理
~~~~~~~~~~~~~~~~~~~~
不用检查节点的写法:
# 去掉 check_x，直接从 START 出发

# 1. 只加两个处理节点
builder.add_node("handle_even", handle_even)
builder.add_node("handle_odd", handle_odd)

# 2. 用 START 作为条件边的起点
builder.add_conditional_edges(START, is_even, {
    True: "handle_even",
    False: "handle_odd"
})

# 3. 处理节点连到 END
builder.add_edge("handle_even", END)
builder.add_edge("handle_odd", END)
"""

'''
我们先在不接入大模型的情况下构建一个加减法图工作流，
我们这里自定义两个简单函数：
    ① 加法函数接收当前State并将其中的x值加1，
    ② 减法函数接收当前State并将其中的x值减2，
然后添加名为addition和subtraction的节点，并关联到两个函数上，最后构建出节点之间的边。
'''

from langgraph.constants import START, END
from langgraph.graph import StateGraph

### 1、定义节点Node(前一步定义状态State是可选项)
#节点1
def addition(state):
    print(f'加法节点收到的初始值:{state}')
    return {"x": state["x"] + 1}

#节点2
def subtraction(state):
    print(f'减法节点收到的初始值:{state}')
    return {"x": state["x"] - 2}

### 2、构建图graph
graph = StateGraph(dict)    #★创建一个图，这个图的 State是一个普通字典，不限制字段名和类型
"""
之前的写法：
    class HelloState(TypedDict):
    name: str
    greeting: str
    ……
    graph = StateGraph(HelloState)      #括号内  ← 传入自定义类
现在的写法：
    graph = StateGraph(dict)            # ← 直接传入 dict     （没有定义之前的状态）
    
对比项	    使用 TypedDict	        使用 dict
代码量	    需要定义类	            更简洁
类型提示	    ✅ IDE 有提示	        ❌ 无提示
字段限制	    ✅ 只能访问定义过的字段	❌ 可以访问任意字段
拼写检查	    ✅ 写错会标红	        ❌ 写错不报错
灵活性	    低（固定结构）	            高（任意结构）
适用场景	    复杂业务、团队协作	        快速测试、简单原型
"""

### 3、 向图构建器中添加节点
# 添加加法运算节点和减法运算节点到构建器中
graph.add_node("additioning", addition)
graph.add_node("subtractioning", subtraction)

### 4、添加边（定义节点之间的执行顺序 edges）
# 设置节点间的依赖关系，形成执行流程图
graph.add_edge(START, "additioning")
graph.add_edge("additioning", "subtractioning")
graph.add_edge("subtractioning", END)

# 打印图的边和节点信息
print("打印图的边信息:\n",graph.edges)     #graph.edges是 StateGraph 对象的内部属性，记录了所有添加的边
"""
输出结果为：
    打印图的边信息:
    {('__start__', 'addition'), ('subtractioning', '__end__'), ('additioning', 'subtraction')}
        #打印的是一个集合，里面套了3个元组
"""
print("-"*35)           #平时不用打印出来边和点信息

print("打印图的节点信息:\n",graph.nodes)    #同上打印点
"""
打印图的节点信息:
 {'additioning': StateNodeSpec(runnable=additioning(tags=None, recurse=True, explode_args=False, func_accepts={}), 
 metadata=None, input_schema=<class 'dict'>, retry_policy=None, cache_policy=None, is_error_handler=False,
  error_handler_node=None, ends=(), defer=False, timeout=None, trace_policy=None), 
  'subtractionting': StateNodeSpec(runnable=subtractionting(tags=None, recurse=True, explode_args=False, func_accepts={}), 
  metadata=None, input_schema=<class 'dict'>, retry_policy=None, cache_policy=None, is_error_handler=False, 
  error_handler_node=None, ends=(), defer=False, timeout=None, trace_policy=None)}
"""
print("①"*20)

## 5.编译图（LangGraph 的"启动开关"）
# 编译图构建器生成计算图
app = graph.compile()

## 6.运行
# invoke()方法只接收状态字典作为核心参数，定义一个初始状态字典，包含键值对"x": 5
initial_state={"x": 5}
# 调用graph对象的invoke方法，传入初始状态，执行图计算流程
result= app.invoke(initial_state)
print(f"最后的结果是:{result}")
"""
输出结果为：
    加法节点收到的初始值:{'x': 5}
    减法节点收到的初始值:{'x': 6}
    最后的结果是:{'x': 4}
"""
print("②"*25)

## 打印图的可视化结构
print(app.get_graph().print_ascii())
"""
+-----------+    
  | __start__ |    
  +-----------+    
         *         
         *         
         *         
  +-------------+  
  | additioning |  
  +-------------+  
         *         
         *         
         *         
+----------------+ 
| subtractioning | 
+----------------+ 
         *         
         *         
         *         
    +---------+    
    | __end__ |    
    +---------+    
None
"""
print("③"*25)

## 打印图的可视化结构，生成更加美观的Mermaid 代码，通过processon 编辑器查看
print(app.get_graph().draw_mermaid())
"""
---
config:
  flowchart:
    curve: linear
---
graph TD;
	__start__([<p>__start__</p>]):::first
	additioning(additioning)
	subtractioning(subtractioning)
	__end__([<p>__end__</p>]):::last
	__start__ --> additioning;
	additioning --> subtractioning;
	subtractioning --> __end__;
	classDef default fill:#f2f0ff,line-height:1.2
	classDef first fill-opacity:0
	classDef last fill:#bfb6fc
"""



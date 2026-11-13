"""演示 LangGraph 的两种流式输出模式：updates（增量）和 values（全量）"""
"""
流图状态:
    使用流模式，并在图执行时流式传输其状态。
    两种流式输出模式updates values
        1、updates：在图的每一步后，将更新流向状态。(增量更新)
        2、values： 在图的每一步后，流出状态的---->全部值。(全量更新)

⭐⭐⭐
实现方式：在最后一步的运行方法中添加参数
    之前是graph.invoke({~})
    现在是graph.stream({~},stream_mode="流式输出的模式")
        #模式有updates和values
"""


from typing import TypedDict
from langgraph.graph import StateGraph, START, END

### 1、状态State
class AtguiguState(TypedDict):
  topic: str
  joke: str


### 2、节点Note
#节点1
def refine_topic(state: AtguiguState):      #设定主题
    return {"topic": state["topic"] + " and cats"}

#节点2
def generate_joke(state: AtguiguState):     #讲一个关于上面主题的笑话
    return {"joke": f"This is a joke about {state['topic']}"}

### 3、新的封装方法，一个对象搞定⭐⭐⭐
def main():     #更现代的 Python 写法（链式调用）
    graph = (
      StateGraph(AtguiguState)      #创建图
      .add_node(refine_topic)       #添加节点
      .add_node(generate_joke)

      .add_edge(START, "refine_topic")      #添加边
      .add_edge("refine_topic", "generate_joke")
      .add_edge("generate_joke", END)

      .compile()                            #编译图
    )

### 4、输出 —— .stream({…},stream_mode="模式")~~~~~~~~~~~~~~~~~~~~~~
# updates在图的每一步后，将更新流向状态。  之前是graph.invoke({"topic": "ice cream"})一次性输出

    ## 4.1 增量输出
    for chunk in graph.stream({"topic": "ice cream"},stream_mode="updates"):
        print(chunk)
    """
    输出结果如下：
        {'refine_topic': {'topic': 'ice cream and cats'}}   
        {'generate_joke': {'joke': 'This is a joke about ice cream and cats'}}
    
    ★可以看出最原始的输出{"topic": "ice cream"}没打印，不是更新的内容（增量输出）
    键名refine_topic和generate_joke来自节点函数名
    """
    print("①"*20)

    """
    
    两种模式输出的字典的键名区别：
        模式	            输出格式	                    键名是什么
        updates	    {节点名: 节点返回的增量}	    节点名（如 refine_topic）
        values	    {完整的 State}	            State 字段名（如 topic、joke）
    """

    ## 4.2 全量输出
    # values在图的每一步后，流出状态的全部值。
    for chunk in graph.stream({"topic": "ice cream"},stream_mode="values"):     #stream_mode="values"
        print(chunk)

    """
    输出结果如下：
        {'topic': 'ice cream'}              #最初的也打印出来了（全量输出）
        {'topic': 'ice cream and cats'}
        {'topic': 'ice cream and cats', 'joke': 'This is a joke about ice cream and cats'}
 
    """


#调用函数~~~~~~~~~~~
if __name__ == "__main__":
    main()
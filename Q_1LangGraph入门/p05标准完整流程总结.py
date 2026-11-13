""" 小总结"""
"""
##定义LangGraph的标准完整流程：
    1.定义状态类State
        LangGraph是状态机，必须先定义存储流转数据的状态(TypedDict/pydantic BaseModel)，这是第一步
        (如果调用大模型，在定义节点前构建模型)
    2、定义节点函数（若使用大模型，在节点函数中调用大模型）
    3.初始化StateGraph实例(传入状态类)，构建状态图
        初始化 StateGraph(State/dict)
    4.添加图节点add_node()
    5.定义边
        普通直线边add_edge()
        条件分支边 add_conditional_edges() —— 复杂图必备（后面讲）
      指定入口节点add_edge(START,"节点名") 或者 set_entry_point ()   
        START是图内置起始标记，add_edge(START,"节点名")  等价于 set_entry_point("节点名")，
        START/END全局常量替代set_entry_point
      指出口节点add_edge("xxx节点",END) 或者 set_finish_point ()
        流程走到末尾，节点无下游边时会自动终止，可选。END是图内置终止标记节点指向END代表流程结束，不用额外配置出口
    6.编译图compile()
    7.传入初始状态，执行/调用工作流
        invoke()方法只接收状态字典作为核心参数，只能传字典
"""
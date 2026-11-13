"""State介绍"""
"""
什么是状态？
    在LangGraph中，State是一个贯穿整个工作流执行过程中的⭐共享数据⭐的结构，代表当前快照，
        State:图的记忆与血液
        单一事实来源(Single Source of Truth)：所有数据通过State在节点间传递和更新。它是LangGraph 的核心。
        Reducer:定义状态如何被安全地、原子化地更新。
        
在 LangGraph 中，状态（State） 是整个工作流的核心记忆和数据载体。
你可以把它想象成一个“全局共享的记事本”。无论流程走到哪个节点，所有节点都在读写这个记事本
    
它存储了从工作流开始到结束的所有必要的信息(历史对话、检索到的文档、工具执行结果等)，
在各个节点中共享，且每个节点都可以修改。状态包含两部分:
    一是图的模式(schema)，二是“规约函数”(reducer functions); 后者指明如何把更新应用到状态上。
    
定义图时做的第一件事就是定义图的State。
State由图的模式(schema)以及指定如何将更新应用于状态的reducer函数组成。
State的模式将作为图中所有 Nodes 和 Edges的输入模式，可以是一个 TypedDict 或 Pydantic 模型。
所有Nodes都会发出对 State的更新，然后使用指定的 reducer函数应用这些更新。
"""
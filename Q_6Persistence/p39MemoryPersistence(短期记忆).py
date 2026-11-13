"""
langgraph-checkpoint：检查点保存器（BaseCheckpointSaver）
的基础接口以及序列化/反序列化接口（SerializerProtocol）。
包含用于实验的内存中检查点实现（InMemorySaver）。
LangGraph 已内置 langgraph-checkpoint。
LangGraph 1.0 持久化存储演示 - 内存存储 (In-Memory)
特点：
    - 数据暂存于内存，程序关闭后丢失
    - 无需额外配置
    - 适用于本地测试和临时验证工作流逻辑
"""
"""
与p24章节讲的节点缓存的区别：
⭐节点缓存是“跳过重复计算”，持久化是“保存状态快照”。
    对比	                        节点缓存	                                持久化（Checkpointer）
    目的	                相同输入跳过重复执行	                                保存每步状态快照
    存什么	            节点的输入 → 输出	                                    整个State 的历史
    解决什么问题	    节省计算时间、Token 消耗	                            支持多轮对话、断点续跑、时间旅行
    配置位置	       add_node(cache_policy=...) + compile(cache=...)	       compile(checkpointer=...)
    什么时候配置              添加节点 和 编译图的时候                        编译图 和 调用invoke的时候
    需要thread_id吗	        ❌ 不需要	                                    ✅ 需要
    能查历史吗	            ❌ 不能	                                    ✅ get_state_history()
"""
"""
⭐⭐⭐实现方式：
1、在编译图时graph = builder.compile()上传参数来持久化
    graph = builder.compile(checkpointer=InMemorySaver())   # 第一步：装记忆
2、配置线程ID用于存储状态。
    config = {"configurable": {"thread_id": "user_13811112222"}}  # 第二步：起名字
3、调用时传 config 指定 thread_id  
    result = graph.invoke({...}, config)                  # 第三步：带名字运行
"""

from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
import operator


### 1、 定义状态
class PersistenceDemoState(TypedDict):
        # operator.add：p17有详解，将元素追加到现有元素中，支持列表、字符串、数值类型的追加，按归约规则合并新旧值
    messages: Annotated[list, operator.add]
    step_count: Annotated[int, operator.add]


### 2、 节点函数
def step_one(state: PersistenceDemoState) -> dict:
    print("执行步骤 1")
    return {
        "messages": ["执行了步骤 1"],
        "step_count": 1
    }


def step_two(state: PersistenceDemoState) -> dict:
    print("执行步骤 2")
    return {
        "messages": ["执行了步骤 2"],
        "step_count": 1
    }


def step_three(state: PersistenceDemoState) -> dict:
    print("执行步骤 3")
    return {
        "messages": ["执行了步骤 3"],
        "step_count": 1
    }


### 3、 构建图图、添加节点、连边
def create_builder():
    builder = StateGraph(PersistenceDemoState)

    builder.add_node("step_one", step_one)
    builder.add_node("step_two", step_two)
    builder.add_node("step_three", step_three)

    builder.add_edge(START, "step_one")
    builder.add_edge("step_one", "step_two")
    builder.add_edge("step_two", "step_three")
    builder.add_edge("step_three", END)

    return builder

### 4、 持久化之存内存
def main():
    print("=== LangGraph 1.0 内存持久化存储演示 ===\n")

    ## 4.1 构件图
    builder = create_builder()      #调用创建图的这个函数，

    ## 4.2 编译图，并给它装上“记忆功能”（内存存储）
    #将检查点保存在内存中，程序退出后丢失。生产环境通常替换为 PostgresSaver / SqliteSaver 等持久化方案
    graph = builder.compile(checkpointer=InMemorySaver())   #⭐
        #checkpointer=	参数，指定“记忆存储”方式；InMemorySaver()	内存存储，把对话历史保存在内存里

    #⭐⭐⭐配置线程ID用于存储状态
    config = {"configurable": {"thread_id": "user_13811112222"}}    #给当前对话会话创建一个“身份证”（唯一ID），用来区分不同用户的对话记录。

    print("1. 首次执行工作流:")
    result = graph.invoke(
        {
                "messages": ["开始执行"],
                "step_count": 0
                },
        config)      #⭐config 配置信息（如 thread_id）	❌ 可选（有 checkpointer 时才需要）
    """
    graph.invoke(input, config)
                   ↑       ↑
                 参数1     参数2（可选）
                 
    参数	      作用	                    是否必须
    input	 传入的初始状态（State）	    ✅ 必须
    config	 配置信息（如 thread_id）	    ❌ 可选（有 checkpointer 时才需要）
    """

    print(f"执行结果result: {result}\n")

    print("2. 检查存储的状态，获取最新状态:")
    saved_state = graph.get_state(config)

    print(f"保存的状态: {saved_state.values}")
    print(f"下一个节点: {saved_state.next}\n")

    #完整历史回溯，获取指定线程的完整执行历史（正序：从最早到最晚,第一步在栈底）
    history = graph.get_state_history(config)     #.get_state_history()	法，获取状态历史,返回列表
        #把 config 里指定的 thread_id 对应的所有对话历史状态都给我取出来。

    # 遍历历史中的每一个检查点快照，可用于：调试、审计、时间旅行回放
    for checkpoint in history:
        print("=" * 50)

        # 该时刻的完整State状态（最核心）
        print(f"当前状态: {checkpoint.values}")

    print("=" * 80)
    print("3. 恢复执行工作流:")
    # 传入了 None 作为输入，对于已执行完毕的工作流：
    # 直接返回最终状态，不会重新执行，因为检查点系统知道该线程已经到达 END
    # 如果工作流 尚未完成（比如中间中断），传入 None 会从断点处 继续执行。这就是 断点续跑 机制。
    result2 = graph.invoke(None, config)
    print(f"恢复执行结果: {result2}\n")

    print("=== 演示结束 ===")

if __name__ == "__main__":
    main()

'''
流程如下:
    === 主流程 ===
    1. builder.compile(checkpointer=InMemorySaver())
       └─ 注册检查点保存器，准备跟踪状态
       
    2. graph.invoke({"messages": ["开始执行"], "step_count": 0}, config)
       │
       ├─ START → step_one
       │   ├─ 输入: {"messages": ["开始执行"], "step_count": 0}
       │   ├─ 执行: print("执行步骤 1")
       │   ├─ 返回: {"messages": ["执行了步骤 1"], "step_count": 1}
       │   ├─ 归约后 State: messages=["开始执行","步骤1"], step_count=1
       │   └─ ★ 自动保存检查点 1
       │
       ├─ step_one → step_two
       │   ├─ 输入: messages=["开始执行","步骤1"], step_count=1
       │   ├─ 执行: print("执行步骤 2")
       │   ├─ 返回: {"messages": ["执行了步骤 2"], "step_count": 1}
       │   ├─ 归约后 State: messages=["开始执行","步骤1","步骤2"], step_count=2
       │   └─ ★ 自动保存检查点 2
       │
       ├─ step_two → step_three
       │   ├─ 输入: messages=["开始执行","步骤1","步骤2"], step_count=2
       │   ├─ 执行: print("执行步骤 3")
       │   ├─ 返回: {"messages": ["执行了步骤 3"], "step_count": 1}
       │   ├─ 归约后 State: messages=["开始执行","步骤1","步骤2","步骤3"], step_count=3
       │   └─ ★ 自动保存检查点 3
       │
       └─ step_three → END → 返回最终 State
    
    3. graph.get_state(config)
       └─ values: {messages: ["开始执行", "步骤1", "步骤2", "步骤3"], step_count: 3}
       └─ next: ()  ← 空，表示执行完毕
    
    4. graph.get_state_history(config)
       └─ 遍历 3 个检查点，每个展示当时的完整 State
    
    5. graph.invoke(None, config)
       └─ 工作流已完成 → 直接返回最终 State，不再执行
'''
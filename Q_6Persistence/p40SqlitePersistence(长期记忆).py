'''
在底层，检查点功能由符合BaseCheckpointSaver接口的检查点对象提供支持。
LangGraph提供了多种检查点实现，所有这些实现都通过独立的、可安装的库来完成，数据库类型的有：
	langgraph-checkpoint-sqlite：使用SQLite数据库（SqliteSaver / AsyncSqliteSaver）存储检查点。
非常适合实验和本地工作流程。需要单独安装。
	langgraph-checkpoint-postgres：使用Postgres数据库（PostgresSaver / AsyncPostgresSaver）
存储检查点，用于LangSmith。非常适合在生产环境中使用。需要单独安装。
......
本次案例，安装sqlite所需依赖
pip install langgraph-checkpoint-sqlite

InMemorySaver：存内存（开发调试）
     ▼
SqliteSaver：存小型数据库（本地实验、单机部署）
     ▼
PostgresSaver：存大数据库（生产环境、多实例、高可用）：很少用，我们更习惯用MySQL，以及向量数据库

'''

import sqlite3
import operator
from typing import TypedDict, Annotated
from langgraph.checkpoint.sqlite import SqliteSaver     #保存到 SQLite 数据库文件里，实现持久化存储
from langgraph.graph import StateGraph,START,END

'''
这是前面 p39MemoryPersistence(短期记忆).py 的升级版 —— 将检查点从 内存存储（短期） 迁移到了 SQLite 数据库（长期）持久化。
⭐⭐⭐
实现方式：
    1、连接数据库（文件不存在时自动创建）
        conn = sqlite3.connect(database="D:\\sqlite_data.db", check_same_thread=False)
    2、创建检查点保存器（把数据库连接包装成 LangGraph 能用的“检查点保存器”）
        sqliteDB = SqliteSaver(conn=conn)
    3、编译时装上（每次节点执行完，状态自动保存到 SQLite 数据库）
        graph = builder.compile(checkpointer=sqliteDB)
'''

### 1、 定义状态
class MyState(TypedDict):
    messages:Annotated[list,operator.add]   #operator.add 是 Python 标准的加法运算符函数，

### 2、 节点函数
def node_1(state:MyState):
    return {"messages":["abc","def"]}

### 3、总函数~~~~~~~~~~~~~~~~~~~~~~~~~~~
def main():
	# 数据存储到D:\\目录下面，需要目录存在
    # check_same_thread=False 允许多线程共享此连接,因为LangGraph 在执行过程中可能会在 不同线程
    # 中访问检查点（例如异步执行、回调、或在事件循环中调度）。如果不设为 False，框架内部切换线程时就会崩溃。
    conn = sqlite3.connect(database="D:\\sqlite_data.db",check_same_thread=False)     #⭐连接数据库
    """
    创建一个SQLite数据库连接，连接到指定路径的数据库文件，并允许多线程访问
        sqlite3.connect()	            调用 sqlite3 模块的 connect 函数，建立数据库连接
        database="D:\\sqlite_data.db"	参数1：数据库文件路径
        check_same_thread=False	        参数2：关闭线程检查，允许多线程同时访问,否则只允许创建连接的线程使用
    """

    sqliteDB = SqliteSaver(conn=conn)   #⭐创建一个 SQLite 检查点保存器（SqliteSaver）实例，用来把 LangGraph 的状态保存到 SQLite 数据库中

    builder = StateGraph(MyState)
    #~~~~~~~~~~~~~~~~~
    builder.add_node("node_1",node_1)

    builder.add_edge(START, "node_1")
    builder.add_edge("node_1", END)

    # 编译图，并给它装上“SQLite记忆功能”，让状态保存到 SQLite 数据库里
    graph = builder.compile(checkpointer=sqliteDB)      #⭐

    # 同一个用户id下，每次执行都会插入一次新数据
    config = {"configurable": {"thread_id": "user-111"}}

    initial_state = graph.get_state(config)
    print(f"Initial state: {initial_state}")
    print("1️"*25)

    # 执行图
    result = graph.invoke({"messages":[]}, config)
    print(f"Result: {result}")
    print("2️⃣" * 25)


    print("============查看执行后的状态==============")
    # 查看执行后的状态
    final_state = graph.get_state(config)
    print()
    print(f"Final state: {final_state}")
    """
    StateSnapshot(
                  values={'messages': ['abc', 'def', 'abc', 'def', 'abc', 'def']}, 
                  next=(), config={'configurable': {'thread_id': 'user-111', 'checkpoint_ns': '', 'checkpoint_id': '1f1d9236-3421-62e1-8007-049c79becf55'}}, 
                  metadata={'source': 'loop', 'step': 7, 'parents': {}}, 
                  created_at='2026-11-05T14:15:43.755337+00:00', 
                  parent_config={'configurable': {'thread_id': 'user-111', 'checkpoint_ns': '', 'checkpoint_id': '1f1d9236-341e-6eb5-8006-f6b58ca36c37'}}, 
                  tasks=(), 
                  interrupts=()
                  )
    """

    conn.close()

if __name__ == '__main__':
    main()

#D盘中创建了 sqlite_data.db文件数据库


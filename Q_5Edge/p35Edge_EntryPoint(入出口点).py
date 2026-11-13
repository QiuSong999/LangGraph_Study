"""
LangGraph入口点演示

入口点定义了图开始执行的第一个节点。
"""
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END


### 1、 定义状态
class AtguiguState(TypedDict):
    value: int
    step: str

### 2、 定义节点函数
def node_a(state: AtguiguState) -> dict:
    """节点A"""
    print("执行节点A")
    print("state[value]:"+str(state["value"]))
    print("state[step]:"+str(state["step"]))
    return {"value": state["value"] + 1, "step": "A执行完毕"}


def node_b(state: AtguiguState) -> dict:
    """节点B"""
    print("执行节点B")
    return {"value": state["value"] * 2, "step": "B执行完毕"}

### 3、 汇总函数
def main():
    """演示入口点"""
    print("=== 入口点演示 ===")

    ## 3.1 创建图
    builder = StateGraph(AtguiguState)

    ## 3.2 添加节点
    #3.2.1 普通节点
    builder.add_node("node_a", node_a)
    builder.add_node("node_b", node_b)

    """
    set_entry_point(node_id) 和 set_finish_point(node_id) 是 LangGraph 为「图对象」提供的配置方法，
    核心作用是将你自定义的业务节点，和内置的 START/END 特殊节点做 “自动绑定”，简化图的入口 / 出口边的定义，
    本质是语法糖（底层还是帮你执行了 add_edge(START, 入口节点) / add_edge(出口节点, END)）
    """

    #3.2.2 出口入口节点
    ####~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    builder.set_entry_point("node_a")   #入口边⭐
    builder.add_edge("node_a", "node_b")
    builder.set_finish_point("node_b")  #出口边⭐
    ####~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    ## 3.3 编译图
    graph = builder.compile()

    ## 3.4 执行图
    result = graph.invoke({"value": 0, "step": "hello"})
    print(f"执行结果: {result}\n")

    print()
    ## 打印图的ascii可视化结构
    print(graph.get_graph().print_ascii())
    print("=================================")
    print()
    # 打印图的可视化结构，生成更加美观的Mermaid 代码，通过processon 编辑器查看
    #print(graph.get_graph().draw_mermaid())


if __name__ == "__main__":
    main()



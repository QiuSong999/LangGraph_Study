'''
LangGraph 多模式流式传输演示
'''

from typing import TypedDict
from langgraph.graph import StateGraph, START, END


### 1、 定义状态类型
class AtguiguState(TypedDict):
    question: str
    answer: str
    confidence: float   # 置信度分数
    steps: list

### 2、 节点函数
def think(state: AtguiguState) -> AtguiguState:
    """思考节点"""
    question = state["question"]
    # 模拟思考过程
    steps = [f"分析问题: {question}", "检索相关知识", "形成初步答案"]
    return {"steps": steps}


def respond(state: AtguiguState) -> AtguiguState:
    """回应节点"""
    question = state["question"]
    # 根据问题生成答案
    if "天气" in question:
        answer = "今天天气晴朗"
        confidence = 0.9
    elif "时间" in question:
        answer = "现在是上午10点"
        confidence = 0.8
    else:
        answer = "这是一个很好的问题"
        confidence = 0.7

    return {
        "answer": answer,
        "confidence": confidence
    }


def reflect(state: AtguiguState) -> AtguiguState:
    """反思节点"""
    answer = state["answer"]
    confidence = state["confidence"]
    steps = state.get("steps", [])

    steps.append(f"验证答案: {answer}")
    steps.append(f"置信度评估: {confidence}")

    if confidence > 0.8:
        conclusion = "高置信度答案"
    elif confidence > 0.5:
        conclusion = "中等置信度答案"
    else:
        conclusion = "低置信度答案"

    steps.append(f"结论: {conclusion}")

    return {"steps": steps}

### 3、一个对象搞定构建图、添加节点，边、编译图
def main():
    # 构建图
    builder = StateGraph(AtguiguState)
    builder.add_node("think", think)
    builder.add_node("respond", respond)
    builder.add_node("reflect", reflect)

    builder.add_edge(START, "think")
    builder.add_edge("think", "respond")
    builder.add_edge("respond", "reflect")
    builder.add_edge("reflect", END)

    graph = builder.compile()

    print("=== LangGraph 多模式流式传输演示 ===\n")

    # 准备输入
    input_state = {
        "question": "今天天气怎么样?",
        "answer": "",
        "confidence": 0.0,
        "steps": []
    }

    print("--- 1. 使用 stream_mode='values' 模式 ---")
    print("显示每一步执行后的完整状态:")
    for chunk in graph.stream(input_state, stream_mode="values"):       #全量
        print(f"  {chunk}")
    """
    --- 1. 使用 stream_mode='values' 模式 ---
    显示每一步执行后的完整状态:
      {'question': '今天天气怎么样?', 'answer': '', 'confidence': 0.0, 'steps': []}        #初始状态也打印出来
      {'question': '今天天气怎么样?', 'answer': '', 'confidence': 0.0, 'steps': ['分析问题: 今天天气怎么样?', '检索相关知识', '形成初步答案']}
      {'question': '今天天气怎么样?', 'answer': '今天天气晴朗', 'confidence': 0.9, 'steps': ['分析问题: 今天天气怎么样?', '检索相关知识', '形成初步答案']}
      {'question': '今天天气怎么样?', 'answer': '今天天气晴朗', 'confidence': 0.9, 'steps': ['分析问题: 今天天气怎么样?', '检索相关知识', '形成初步答案', '验证答案: 今天天气晴朗', '置信度评估: 0.9', '结论: 高置信度答案']}
    """
    print("①"*20)

    print("--- 2. 使用 stream_mode='updates' 模式 ---")
    print("只显示每一步的状态更新:")
    for chunk in graph.stream(input_state, stream_mode="updates"):      #增量
        print(f"  {chunk}")
    """
    --- 2. 使用 stream_mode='updates' 模式 ---
    只显示每一步的状态更新:
      {'think': {'steps': ['分析问题: 今天天气怎么样?', '检索相关知识', '形成初步答案']}}
      {'respond': {'answer': '今天天气晴朗', 'confidence': 0.9}}
      {'reflect': {'steps': ['分析问题: 今天天气怎么样?', '检索相关知识', '形成初步答案', '验证答案: 今天天气晴朗', '置信度评估: 0.9', '结论: 高置信度答案']}}
    """
    print("②"*20)

    print("--- 3. 同时使用stream_mode=[values,updates]多种流模式 ---")
    print("同时显示完整状态和状态更新:")
    for mode, chunk in graph.stream(input_state, stream_mode=["values", "updates"]):    #增量+全量
        print(f"  [{mode}]: {chunk}")
    """
    --- 3. 同时使用stream_mode=[values,updates]多种流模式 ---
    同时显示完整状态和状态更新:
        [values]: {'question': '今天天气怎么样?', 'answer': '', 'confidence': 0.0, 'steps': []}
        [updates]: {'think': {'steps': ['分析问题: 今天天气怎么样?', '检索相关知识', '形成初步答案']}}
        [values]: {'question': '今天天气怎么样?', 'answer': '', 'confidence': 0.0, 'steps': ['分析问题: 今天天气怎么样?', '检索相关知识', '形成初步答案']}
        [updates]: {'respond': {'answer': '今天天气晴朗', 'confidence': 0.9}}
        [values]: {'question': '今天天气怎么样?', 'answer': '今天天气晴朗', 'confidence': 0.9, 'steps': ['分析问题: 今天天气怎么样?', '检索相关知识', '形成初步答案']}
        [updates]: {'reflect': {'steps': ['分析问题: 今天天气怎么样?', '检索相关知识', '形成初步答案', '验证答案: 今天天气晴朗', '置信度评估: 0.9', '结论: 高置信度答案']}}
        [values]: {'question': '今天天气怎么样?', 'answer': '今天天气晴朗', 'confidence': 0.9, 'steps': ['分析问题: 今天天气怎么样?', '检索相关知识', '形成初步答案', '验证答案: 今天天气晴朗', '置信度评估: 0.9', '结论: 高置信度答案']}
    """
    print("③"*20)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    print("--- 4. 使用 debug 模式 ---")
    print("显示详细的调试信息:")
    try:
        for chunk in graph.stream(input_state, stream_mode="debug"):    #⭐输出极其详尽的底层运行日志（执行轨迹）很少用，用于调试的
            print(f"  {chunk}")
    except Exception as e:
        print(f"  Debug模式可能需要特殊配置: {e}")
"""
--- 4. 使用 debug 模式 ---
显示详细的调试信息:
  {'step': 1, 'timestamp': '2026-09-06T09:18:41.058607+00:00', 'type': 'task', 'payload': {'id': '24479a16-8d13-4c1f-cb95-31e088eff3f1', 'name': 'think', 'input': {'question': '今天天气怎么样?', 'answer': '', 'confidence': 0.0, 'steps': []}, 'triggers': ('branch:to:think',)}}
  {'step': 1, 'timestamp': '2026-09-06T09:18:41.058607+00:00', 'type': 'task_result', 'payload': {'id': '24479a16-8d13-4c1f-cb95-31e088eff3f1', 'name': 'think', 'error': None, 'result': {'steps': ['分析问题: 今天天气怎么样?', '检索相关知识', '形成初步答案']}, 'interrupts': []}}
  {'step': 2, 'timestamp': '2026-09-06T09:18:41.058607+00:00', 'type': 'task', 'payload': {'id': '56a67d6e-ebff-636c-6bd9-80970191e113', 'name': 'respond', 'input': {'question': '今天天气怎么样?', 'answer': '', 'confidence': 0.0, 'steps': ['分析问题: 今天天气怎么样?', '检索相关知识', '形成初步答案']}, 'triggers': ('branch:to:respond',)}}
  {'step': 2, 'timestamp': '2026-09-06T09:18:41.058607+00:00', 'type': 'task_result', 'payload': {'id': '56a67d6e-ebff-636c-6bd9-80970191e113', 'name': 'respond', 'error': None, 'result': {'answer': '今天天气晴朗', 'confidence': 0.9}, 'interrupts': []}}
  {'step': 3, 'timestamp': '2026-09-06T09:18:41.058607+00:00', 'type': 'task', 'payload': {'id': 'd0a23bf1-714a-f51e-d185-7db18da0182c', 'name': 'reflect', 'input': {'question': '今天天气怎么样?', 'answer': '今天天气晴朗', 'confidence': 0.9, 'steps': ['分析问题: 今天天气怎么样?', '检索相关知识', '形成初步答案']}, 'triggers': ('branch:to:reflect',)}}
  {'step': 3, 'timestamp': '2026-09-06T09:18:41.059607+00:00', 'type': 'task_result', 'payload': {'id': 'd0a23bf1-714a-f51e-d185-7db18da0182c', 'name': 'reflect', 'error': None, 'result': {'steps': ['分析问题: 今天天气怎么样?', '检索相关知识', '形成初步答案', '验证答案: 今天天气晴朗', '置信度评估: 0.9', '结论: 高置信度答案']}, 'interrupts': []}}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
模式	    你看到的内容	                    主要用途
values	每一步的完整 State	            看数据全貌
updates	每一步的增量更新	                看节点改了什么
debug	任务调度、检查点、耗时等底层事件	    开发调试、性能分析

debug官方文档提到，这个模式适合开发阶段排查问题。比如你想知道：
    1、某个节点到底有没有被执行？
    2、节点的输入/输出具体是什么？
    3、图的执行步骤和顺序是否符合预期？
注意：因为输出信息非常庞杂（你代码里的输出也印证了这点），它通常只建议在开发和调试阶段使用，生产环境一般不会开启。
"""

if __name__ == "__main__":
    main()

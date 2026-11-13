"""
三种不同的数据结构可视化与输出方案：
    #先app.get_graph():从编译好的应用程序（app）中，把底层的图结构信息“拿出来”,它是可视化的起点
    1、打印图的ascii可视化结构                方式：app.get_graph().print_ascii()       #图结构信息后面加.print_ascii()
    2、打印图的Mermaid代码可视化结构           方式：app.get_graph().draw_mermaid()      #图结构信息后面加draw_mermaid()
      并通过processon编辑器查看
    3、生成PNG并写入文件
        方式：具体看下面代码演示，app.get_graph().draw_mermaid_png()……

LangGraph提供了多种图表可视化方式，帮助开发者更好地理解和调试工作流。
通过graph.get_graph()方法可以获图的结构信息，包括节点和边的详细信息。
基于这个信息，可以使用如下方式进行可视化:
    生成Mermaid代码来可视化图结构。
    生成简单的ASCII文本图表，但需要安装额外的依赖。
"""
"""
★★★
构建 LangGraph 应用的核心流程，可以简单概括为以下几步：          实现方法
    1、定义状态：确定数据长什么样（设计"箱子"）。             —— 定义状态类
    2、定义节点：编写处理数据的函数（招募"工人"）。           —— 定义节点函数
    3、构建图：将节点加入图中，并用边连接它们（组装流水线）。   —— graph = StateGraph(State)
    4、图上添加节点、构建边                               —— graph.add_node()和graph.add_edge()
    5、编译图：将图编译为可执行程序并启动（按下开关）。        —— app = graph.compile()
    6、运行                                            —— app.invoke()
"""

# 首先要pip install grandalf
### 0、导入依赖
from typing import TypedDict                            # TypedDict：定义 State 的结构，提供类型提示
from langgraph.graph import StateGraph, START, END      # StateGraph	LangGraph 的核心类，用于构建状态图
#START:特殊节点，表示图的入口（从哪里开始执行）；   END:特殊节点，表示图的出口（执行结束）
import uuid                                             #uuid生成随机文件名，避免图片覆盖


"""
何为LangGraph？
    LangGraph = LangChain + 图排版 + 状态机
    LangGraph四大元素：State状态，Nodes节点，Edge边,Graph图
"""

### 1．定义State对象/状态类(其实是个字典，用来存储信息，状态就是不断修正的存储)，
    #官方推荐必须定义状态，但是可以不定义
class HelloState(TypedDict):    #类的名字不是固定的，但继承TypedDict是固定的
    name: str                   #定义的变量，并限制变量类型
    greeting: str
    #app.invoke({"name":"z3"})后 LangGraph 收到你传入的字典 state = {"name": "z3"}
    # Graph中的Node，不是彼此直接传数据，而是通过同一个State传递数据。
    #State不是“所有变量的集合”，而是“需要在 Workflow 不同节点之间传递的数据”。


### 2.定义节点Node(就是干活的函数)
#节点1
def greet(helloState: HelloState) -> dict:      #将来传入的参数名为 helloState，类型是 HelloState（就是上面定义的类）
    name = helloState["name"]                   #取出helloState状态字典中，键=name的值
    #name 的值是在调用时传入的！ 上面一步的定义类（只是"蓝图"）
    return {"greeting": f"你好,{name}"}          #greeting是键，f"你好,{name}"是值
        #Node执行完以后，需要把它产生的 State 更新结果交还给 Graph
"""
节点1返回{'greeting': '你好,z3'}               #return helloState 效果同上
⭐⭐但是经过节点1返回{'greeting': '你好,z3'}后，LangGraph 立刻自动合并状态为{'name': 'z3', 'greeting': '你好,z3'}
~~~~~~~~~~
也可以返回helloState状态，如下写法：
    def greet(helloState: HelloState) -> dict:
        helloState["greeting"] = f"你好,{helloState['name']}"     # 必须要先修改
        return helloState           # 才能返回完整的状态  
 ~~~~~~~~                                           
两种返回return的方式：
   方式1：             方式2：
读取完整 State       读取 State
    ↓                   ↓
修改 State         只返回需要更新的字段 
    ↓                   ↓
返回完整 State     LangGraph 合并到 State  
"""

#节点2
def add_emoji(helloState:HelloState) -> dict:       #虽然参数也为helloState，但和上面greet函数的参数代表不同意思
    greeting = helloState["greeting"]               #从节点1返回的中取键为greeting所对应的值，即“你好,z3”
    return {"greeting": greeting + "  。。。😄"}     #等价于 {"greeting": f"{greeting} 。。。😄"}
"""
经过节点1后，传入的状态为{"name":"z3"，'greeting': '你好,z3'}         
⭐⭐再经过经过节点2返回{'greeting': '你好,z3 。。。😄'}后，
LangGraph 立刻自动合并状态并更新为：
    {'name': 'z3', 'greeting': '你好,z3 。。。😄'}    #替代原来的greeting内容
"""
### 3.构建图graph
graph = StateGraph(HelloState)      # StateGraph()创建一个图（工作流），这个图使用 HelloState 这种数据格式来存储和传递状态

"""
StateGraph 是最常用、最基础的构建类，但 LangGraph 为了应对不同的复杂场景，还提供了其他几种"图纸"
    1.StateGraph（最常用）
        适用场景：绝大多数情况。
        特点：你需要显式定义状态结构（如 HelloState），然后手动添加节点和边。它给了你最大的控制权。
        代码：graph = StateGraph(MyState)
    2.MessageGraph（专用于对话）
        适用场景：纯粹的聊天机器人，且状态仅仅就是"消息列表"。
        特点：它内置了状态定义（就是一个消息列表），你不需要自己写 TypedDict 来定义状态。它简化了聊天应用的创建。
        代码：graph = MessageGraph()
    3. Command / 动态路由（进阶）
        适用场景：当下一步去哪里取决于上一步的具体计算结果（比如 AI 决定是查数据库还是直接回答）。
        特点：这通常不是通过构造函数改变的，而是在 add_edge 时使用条件逻辑，或者在节点返回时直接指定下一步。
        
90% 的情况：用 StateGraph 就够了，它是标准答案。
特殊情况：如果你只是写个简单的聊天流，不想定义状态类，可以用 MessageGraph
"""

### 4.添加节点和构建边
# 在图中添加2个节点（步骤2之前定义的节点添加上去）:
# 将一个 Python/节点 函数（或可调用对象）绑定到一个唯一的节点名称上，使其成为图工作流中的一个“工作站”
graph.add_node("greeting",greet)            #.add_node()	方法	图的"添加节点"方法
graph.add_node("add_emojing",add_emoji)     #第一个参数是创建的节点的名字，第二参数是节点函数，即上一步定义的节点函数名

# 添加边（点连在一起形成边）
# 该代码定义了数据流动的方向和顺序。add_edge 的作用就是告诉图：“当 A 做完后，接下来去做 B”
graph.add_edge(START, "greeting")       #.add_edge(A,B)  :定义节点之间的执行顺序（节点A 执行完后，去执行节点 B）
graph.add_edge("greeting","add_emojing")
graph.add_edge("add_emojing",END)
"""⭐⭐⭐ State = 在流程中传递的数据 ；Node = 对 State 做事情 ；Edge = 决定 Node 执行顺序"""


"""
在 LangGraph 中，START 和 END 是框架预定义的特殊常量（Constant），而不是普通的字符串
必须大写？
    它们是特殊的“占位符”
        START 和 END 代表的是图的入口点和出口点。LangGraph 内部通过这两个特定的对象来识别流程从哪里开始、在哪里结束。
        如果你写成小写的 "start" 或 "end"，系统会认为你是在引用一个名为 "start" 的普通节点，而不是系统的入口，从而导致报错或流程无法启动。
    本质是对象，不是字符串
        虽然你在代码里看起来像是在传参，但它们实际上是从 langgraph.graph 模块导入的特殊对象。
"""


### 5.编译图（LangGraph 的"启动开关"）
app = graph.compile()       #.compile()	把图转换成可执行程序
    #app：LangGraph 编译后的应用对象："把设计好的图纸（graph）真正建成可运行的程序（app）
"""
构建图 和 编译图 不是一回事
    graph = StateGraph(HelloState) 可以理解成：正在搭建中的 Graph，后面要不断添加节点、边。（负责搭建）
    app = graph.compile() 可简单理解成：把我们刚才搭建好的 Graph 编译成一个真正可以执行的 Graph。（负责执行）
~~~~~~
流程：
    graph 构建图
        ↓
    不断向图中添加 Node、Edge、Conditional Edge
        ↓
    完整的流程图
        ↓
    compile() ——（演绎图）
        ↓
    app  —— （形成可执行的Graph）
        ↓
    app.invoke(state) —— 不能graph.invoke(state)，因为graph只是一个图的构建器
        ↓
    真正执行

即 StateGraph 用来搭图，compile() 把图编译成可执行Graph，invoke() 执行 app
"""

### 6.运行
# invoke()方法只接收状态字典作为核心参数
result = app.invoke({"name":"z3"})  #上传的是字典，invoke()方法只接收状态字典作为核心参数
#一旦.invoke()立马找START，从START开始运行 →"greeting" → "add_emojing" → END
print(result)                       #{'name': 'z3', 'greeting': '你好,z3  。。。😄'}
print("-"*25)
print(result["greeting"])           #你好,z3  。。。😄
print("①"*35)

"""
执行流程：
    初始状态：{'name': 'z3'}     #invoke里面输入的就是初始状态
    节点1返回：{'greeting': '你好,z3'}
    合并：把返回的字典 merge 进去 → 此时的状态为{'name': 'z3', 'greeting': '你好,z3'}
    节点2返回：{'greeting': '你好,z3 。。。😄'}
    合并：发现返回的字典里有greeting这个键，直接覆盖旧值 → 此时状态为{'name': 'z3', 'greeting': '你好,z3 。。。😄'}
    所以"积累"指的是：全局状态里已有的键会被保留，返回字典里的键会被合并进去。而不是把每次返回的字典都堆叠在一起。
"""

### 7 打印图的边和节点信息
## 7.1 打印图的ascii可视化结构 —— (对应第一种数据结构可视化与输出方案)
print(app.get_graph().print_ascii())
#⭐⭐⭐.get_graph()：从我们编译好的应用程序（app）中，把底层的图结构信息“拿出来”,它是可视化的起点，返回一个包含节点和边信息的图对象
#⭐⭐⭐.print_ascii()：翻译成字符画,调用图对象的内置方法，将图的结构转换成由 +, -, |, v 等纯文本符号组成的“字符画”
print("②"*50)

"""
输出内容是：
   +-----------+   
   | __start__ |    #四个-表示“隐式存在的虚拟节点”，你不需要定义它们 
   +-----------+   
          *        
          *        
          *        
    +----------+   
    | greeting |   
    +----------+   
          *        
          *        
          *        
   -------------+  
    add_emojing |  
   -------------+  
          *        
          *        
          *        
    +---------+    
    | __end__ |    
    +---------+  
"""


## 7.2 打印图的Mermaid代码可视化结构并通过https://www.processon.com/mermaid编辑器查看 —— (对应第二种数据结构可视化与输出方案)
print(app.get_graph().draw_mermaid())
#⭐⭐⭐.get_graph()	获取图结构对象（包含所有节点和边）
#⭐⭐⭐.draw_mermaid()	生成 Mermaid 格式的流程图代码
print("③"*50)

"""
输出内容是：
    config:
      flowchart:
        curve: linear
    ---
    graph TD;
        __start__([<p>__start__</p>]):::first
        greeting(greeting)
        add_emojing(add_emojing)
        __end__([<p>__end__</p>]):::last
        __start__ --> greeting;
        greeting --> add_emojing;
        add_emojing --> __end__;
        classDef default fill:#f2f0ff,line-height:1.2
        classDef first fill-opacity:0
        classDef last fill:#bfb6fc
"""

#7.3 生成 PNG并写入文件 ，一般需要开启科学上网（把 LangGraph 流程图导出为 PNG 图片文件） —— (对应第三种数据结构可视化与输出方案)
png_bytes = app.get_graph().draw_mermaid_png(max_retries=2,retry_delay=2.0) #失败最多重试2次，每次重试前等2秒
# app.get_graph() → 获取图结构；
# .draw_mermaid_png() → 生成 PNG 图片的二进制数据

output_path = "langgraph" + str(uuid.uuid4())[:8] + ".png"  # "langgraph" 文件名前缀
#str(uuid.uuid4())[:8]	生成一个随机 8 位字符串（如 "a1b2c3d4"）
#"langgraph" + ... + ".png"	拼接成文件名，如 langgraph_a1b2c3d4.png
# 这行代码只是生成一个“文件名字符串”，并没有真正创建文件。

with open(output_path, "wb") as f:      #"wb"  以二进制写入模式打开文件
    f.write(png_bytes)      #f.write(png_bytes)	把图片二进制数据写入文件
print(f"图片已生成：{output_path}")
#查看本目录下的langgraph69645117.png图片，就是output_path

"""
上面第3种方式，容易bug,时好时坏，域名解析失败，程序无法解析 mermaid.ink 域名，
连不上在线绘图接口，所以导出 Mermaid 图片失败。
ValueError: Failed to reach https://mermaid.ink  
API while trying to render your graph after 1 retries. 
To resolve this issue:
1. Check your internet connection and try again
2. Try with higher retry settings: `draw_mermaid_png(..., max_retries=5, retry_delay=2.0)`
3. Use the Pyppeteer rendering method which will render your graph locally in a browser: 
`draw_mermaid_png(..., draw_method=MermaidDrawMethod.PYPPETEER)`
"""


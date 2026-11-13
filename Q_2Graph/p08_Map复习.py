from typing import TypedDict
from langgraph.constants import START, END
from langgraph.graph import StateGraph

# 1. 定义状态机对象Obj，等价于业务实体entity，或者叫当前数据快照
class GraphStateObj(TypedDict):
    process_data: dict


if __name__ == '__main__':
    obj = GraphStateObj()

    # 第一种写法：[key]
    obj["k1"] = "v1"  # set k1 v1
    obj["k2"] = "v2"

    print(obj.keys())        #拿全部的key       dict_keys(['k1', 'k2'])
    print(obj.values())      #拿全部的value     dict_values(['v1', 'v2'])
    print("①"*20)

    #写法2：get方法
    print(obj.get("k1"))
    # print(obj.get("k3"))
    print("②" * 20)

    print(obj["k1"])
    # print(obj["k3"])# KeyError: 'k3'
    print("③" * 20)

    # 遍历键
    for key in obj:
        print(key)
    print("-"*35)
    # 遍历键+值
    for k, v in obj.items():        #★★★
        print(f"{k}: {v}")
        """
        obj 是你的状态对象（本质上是个字典）。
        .items() 是字典的一个内置方法。它会把字典里的每一对数据打包成一个个元组 (key, value)
        """

    #
    #








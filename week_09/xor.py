from typing import List, Union, Any


class Node:
    weights: list[float]

    def __init__(self, weights: list, value: float = None):
        self.value = value
        self.weights = weights


class Layer:
    bias: float
    # index: int
    nodes: list[Node]

    def __init__(self, index: int, nodes: list, bias: float):
        # self.index = index
        self.nodes = nodes
        self.bias = bias


class XOR:
    layers: list[Layer]

    # [
    #     [
    #         [w11, w12],
    #         [w21, w22],
    #         [b1, b2]
    #     ],
    #     [
    #         [w11],
    #         [w21],
    #         [b1]
    #     ],
    # ]

    def __init__(self, weights):

        w_input1 = weights[0][0]
        w_input2 = weights[0][1]
        w_bias = weights[0][2]

        self.weights = weights
        self.layers = [
            Layer(0, [Node(weights=[w_input1, w_input2])], bias=w_bias)
        ]

        self.layers = []
        for i, weights in weights:
            nodes = []
            layer_bias = weights.pop(len(weights) - 1)
            for weight in weights:
                nodes.append(Node())
            layer = Layer(nodes=nodes, bias=layer_bias)
            self.layers.append(layer)

    def calculate(self, input1: float, input2: float) -> int:

        layers = [
            Layer(0, [Node])
        ]
        for layer in self.weights:
            for weights in layer:  # neurons' weights
                dot = input1 * weights[0] + input2 * weights[1] + weights
                out = 1.0 if dot > 0.5 else 0.0

        w2 = [7.92029005, -7.657149]
        bias2 = 3.84542829
        dot2 = input1 * w2[0] + input2 * w2[1] + bias2
        out2 = 1.0 if dot2 > 0.5 else 0.0

        w3 = [-11.29050389, -11.27539016]
        bias3 = 16.66356337
        dot3 = out1 * w3[0] + out2 * w3[1] + bias3
        out3 = 1.0 if dot3 > 0.5 else 0.0

        return int(out3)

    #
    # def calculate(self, input1: float, input2: float) -> int:
    #     w1 = [-7.49719117, 7.78863945]
    #     bias1 = 3.75568751
    #     dot1 = input1 * w1[0] + input2 * w1[1] + bias1
    #     out1 = 1.0 if dot1 > 0.5 else 0.0
    #
    #     w2 = [7.92029005, -7.657149]
    #     bias2 = 3.84542829
    #     dot2 = input1 * w2[0] + input2 * w2[1] + bias2
    #     out2 = 1.0 if dot2 > 0.5 else 0.0
    #
    #     w3 = [-11.29050389, -11.27539016]
    #     bias3 = 16.66356337
    #     dot3 = out1 * w3[0] + out2 * w3[1] + bias3
    #     out3 = 1.0 if dot3 > 0.5 else 0.0
    #
    #     return int(out3)


def xor(weights: list, input1: float, input2: float) -> int:
    w1 = [weights[0][0][0], weights[0][1][0]]
    bias1 = weights[0][2][0]
    dot1 = input1 * w1[0] + input2 * w1[1] + bias1
    out1 = 1.0 if dot1 > 0.5 else 0.0

    w2 = [weights[0][0][1], weights[0][1][1]]
    bias2 = weights[0][2][1]
    dot2 = input1 * w2[0] + input2 * w2[1] + bias2
    out2 = 1.0 if dot2 > 0.5 else 0.0

    w3 = [weights[1][0][0], weights[1][1][0]]
    bias3 = weights[1][2][0]
    dot3 = out1 * w3[0] + out2 * w3[1] + bias3
    out3 = 1.0 if dot3 > 0.5 else 0.0

    return int(out3)


if __name__ == '__main__':
    # input1 = float(input("enter first input  : "))
    # input2 = float(input("enter second input : "))
    # print(xor(input1, input2))

    weights = [
        [
            [-7.49719117, 7.92029005],
            [7.78863945, -7.657149],
            [3.75568751, 3.84542829]
        ],
        [
            [-11.29050389],
            [-11.27539016],
            [16.66356337]
        ]
    ]

    cases = [
        [0, 0, 0],
        [0, 1, 1],
        [1, 0, 1],
        [1, 1, 0],
        [0.27, 0.15, 0],
        [0.22, 0.85, 1],
        [0.83, 0.28, 1],
        [0.77, 0.55, 0],
    ]
    for case in cases:
        print("%s ^ %s => %s (%s)" % (
            case[0], case[1], case[2], ('OK' if xor(weights, case[0], case[1]) == case[2] else 'KO')))

import pandas as pd

df = pd.DataFrame()

df['sale_time'] = ((df['sold_datetime'] - df['self_evaluation_completed_datetime']).
                   dt.total_seconds()) / (60 * 60)  # time taken by Auto1 to sell the car through auction

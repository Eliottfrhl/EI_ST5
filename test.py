import xml.etree.ElementTree as ET

path = "train-gate.xml"
"""
with open(path, "r") as file:
    data = file.read()

print(data)"""


def getGraph(template):
    Graph = {
        "node": [],
        "edge": {}
    }
    locations = template.findall('.//location')
    transitions = template.findall('.//transition')

    for location in locations:
        Graph["node"].append(location.get('id'))

    for transition in transitions:
        source = transition.find('source').get('ref')
        target = transition.find('target').get('ref')
        transition_id = transition.get('id')
        Graph["edge"][transition_id] = (transition_id, source, target)

    return Graph


def neighbours(graph, node):
    neighbours = []
    for edge in graph["edge"]:
        if edge[1] == node:
            neighbours.append(edge[2], edge[0])
    return neighbours


def dfs(node, visited, path):
    visited[node] = True
    path.append(node)

    neighbours = neighbours(graph, node)
    if neighbours is not None:
        for neighbour in neighbours:
            if neighbour not in visited:
                dfs(neighbour, visited.copy(), path.copy())
            elif neighbour in path:
                cycle_start = path.index(neighbour)
                cycle = path[cycle_start:]
                cycles.append(cycle)


def find_cycles(graph):
    cycles = []
    nodes = graph['node']

    for node in nodes:
        dfs(node, {}, [])

    return cycles


def main():
    tree = ET.parse(path)
    root = tree.getroot()

    templates = root.findall('.//template')

    for template in templates:
        Graph = getGraph(template)
        print(Graph)
        cycles = find_cycles(Graph)
        print(cycles)


main()

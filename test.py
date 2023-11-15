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
        Graph["edge"][transition_id] = (source, target)

    return Graph


def find_cycles(graph):
    def dfs(node, visited, path):
        visited[node] = True
        path.append(node)

        if node in graph['edge']:
            neighbors = graph['edge'][node]
            for neighbor in neighbors:
                if neighbor not in visited:
                    dfs(neighbor, visited.copy(), path.copy())
                elif neighbor in path:
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:]
                    cycles.append(cycle)

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


if __name__ == "__main__":
    main()

import networkx as nx
import xml.etree.ElementTree as ET
import zlib
import base64
import copy


def parse_template(template):
    G = nx.DiGraph()

    locations = template.findall('.//location')
    transitions = template.findall('.//transition')

    for location in locations:
        G.add_node(location.get('id'))

    for transition in transitions:
        source = transition.find('source').get('ref')
        target = transition.find('target').get('ref')
        G.add_edge(source, target, transition_id=transition.get('id'))

    return G


def parralels(template):
    transitions = template.findall('.//transition')
    trans = {}
    for transition in transitions:
        source = transition.find('source').get('ref')
        target = transition.find('target').get('ref')
        transition_id = transition.get('id')
        trans[transition_id] = (source, target)

    flipped = {}

    for key, value in trans.items():
        if value not in flipped:
            flipped[value] = [key]
        else:
            flipped[value].append(key)

    parralels = []

    for key, value in flipped.items():
        if len(value) > 1:
            parralels.append(value)
    return parralels


def find_cycles(template):
    G = parse_template(template)
    cycles = list(nx.simple_cycles(G))
    parra = parralels(template)
    return cycles, G, parra


def resetChecker(cycle, root):
    transitions = root.findall('.//transition')
    for transition in cycle[1]:
        xml_trans = transitions[0]
        lab = xml_trans.find("label").text
        print(lab)
    return False


def main():
    tree = ET.parse('train-gate.xml')
    root = tree.getroot()
    transitions = root.findall('.//transition')
    print(transitions)
    templates = root.findall('.//template')
    results = {}
    for template in templates:
        template_name = template.find('name').text
        cycles, G, parra = find_cycles(template)
        print(f"Cycles in {template_name}:")
        result = []
        for cycle in cycles:
            transitions = []
            for i in range(len(cycle)):
                source = cycle[i]
                target = cycle[(i + 1) % len(cycle)]
                edge_data = tree.find(
                    f".//transition[@id='{G[source][target]['transition_id']}']")
                transition_id = edge_data.get('id')
                transitions.append(transition_id)
            result.append([cycle, transitions])
            """print(f"  Locations: {', '.join(cycle)}, Transitions: {
                  ', '.join(transitions)}")"""
        for cycle in copy.deepcopy(result):
            for parralel in parra:
                for par in parralel:
                    if par in cycle[1]:
                        idx = cycle[1].index(par)
                        par_idx = parralel.index(par)
                        new_cycle = [cycle[0], cycle[1]
                                     [:idx]+[parralel[1-par_idx]]+cycle[1][idx+1:]]
                        result.append(new_cycle)
        results[template_name] = result
    return results


"""if __name__ == "__main__":
    main()
"""

tree = ET.parse('train-gate.xml')
root = tree.getroot()

resetChecker(["id3", "id1"], root)

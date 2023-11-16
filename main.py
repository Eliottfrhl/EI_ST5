import networkx as nx
import xml.etree.ElementTree as ET
import zlib
import base64
import copy
from time import sleep


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


def get_clock_name(text, value):
    text = text.split(",")
    for index in range(len(text)):
        while text[index][0] == " ":
            text[index] = text[index][1:]
        while text[index][-1] == " ":
            text[index] = text[index][:len(text[index])-1]
    for assignment in text:
        if value in assignment:
            index = assignment.index(value[0])
            if assignment[index-1] == ":":
                index -= 1
            return assignment[:index]


def suffCond(cycle, root):
    result = {}
    for transition in cycle[1]:
        xml_trans = root.findall(".//transition[@id='" + transition + "']")
        assignments = xml_trans[0].findall(".//label[@kind='assignment']")
        guards = xml_trans[0].findall(".//label[@kind='guard']")
        for assignment in assignments:
            if "=0" in assignment.text:
                clock_name = get_clock_name(assignment.text, "=0")
                if clock_name in result.keys():
                    result[clock_name][0] = True
                else:
                    result[clock_name] = [True, False]
        for guard in guards:
            if ">" in guard.text:
                clock_name = get_clock_name(guard.text, ">")
                if clock_name in result.keys():
                    result[clock_name][1] = True
                else:
                    result[clock_name] = [False, True]
    if result == {}:
        return False
    else:
        for name, booleans in result.items():
            if booleans == [True, True]:
                return True
        return False


def main():
    tree = ET.parse('train-gate.xml')
    root = tree.getroot()
    transitions = root.findall('.//transition')
    templates = root.findall('.//template')
    results = {}
    for template in templates:
        template_name = template.find('name').text
        cycles, G, parra = find_cycles(template)
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
    results_zeno = {}
    results_potential_zeno = {}
    for name, template in results.items():
        results_zeno[name] = []
        results_potential_zeno[name] = []
        for cycle in template:
            if suffCond(cycle, root):
                results_zeno[name].append(cycle)
            else:
                results_potential_zeno[name].append(cycle)

    return results, results_zeno, results_potential_zeno


"""if __name__ == "__main__":
    main()
"""


"""tree = ET.parse('train-gate.xml')
root = tree.getroot()

resetChecker(["id3", "id1"], root)"""
"""string = "    x:=0   , y<=10    "
print(string)
clock = get_clock_name(string, "<")
print(clock)"""

"""tree = ET.parse('train-gate.xml')
root = tree.getroot()

cycle = [[], ["id7", "id6"]]

boolean = suffCond(cycle, root)

print(boolean)"""

r, rz, rpz = main()
print("All cycles found :")
print(r)
print("All cycles that verify the sufficient condition :")
print(rz)
print("All cycles that do not verify the sufficient condition :")
print(rpz)

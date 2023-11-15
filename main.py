import networkx as nx
import xml.etree.ElementTree as ET


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


def find_cycles(template):
    G = parse_template(template)
    cycles = list(nx.simple_cycles(G))
    return cycles, G


def main():
    tree = ET.parse('train-gate.xml')
    root = tree.getroot()

    templates = root.findall('.//template')

    for template in templates:
        template_name = template.find('name').text
        cycles, G = find_cycles(template)
        print(f"Cycles in {template_name}:")
        for cycle in cycles:
            transitions = []
            for i in range(len(cycle)):
                source = cycle[i]
                target = cycle[(i + 1) % len(cycle)]
                edge_data = tree.find(
                    f".//transition[@id='{G[source][target]['transition_id']}']")
                transition_id = edge_data.get('id')
                transitions.append(transition_id)
            print(f"  Locations: {', '.join(cycle)}, Transitions: {
                  ', '.join(transitions)}")


if __name__ == "__main__":
    main()

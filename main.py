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


def parallels(template):
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

    parallels = []

    for key, value in flipped.items():
        if len(value) > 1:
            parallels.append(value)
    return parallels


def find_cycles(template):
    G = parse_template(template)
    cycles = list(nx.simple_cycles(G))
    para = parallels(template)
    return cycles, G, para


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
            assignment_text = "".join(assignment.text.split(" "))
            if "=0" in assignment_text:
                clock_name = get_clock_name(assignment_text, "=0")
                if clock_name in result.keys():
                    result[clock_name][0] = True
                else:
                    result[clock_name] = [True, False]
        for guard in guards:
            guard_text = "".join(guard.text.split(" "))
            if ">" in guard_text:
                clock_name = get_clock_name(guard_text, ">")
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


def syncCond(rpz, rnz, root):
    rnz_copy = copy.deepcopy(rnz)
    for name, template in rpz.items():
        for cycle in template:
            for transition in cycle[1]:
                xml_trans = root.findall(
                    ".//transition[@id='" + transition + "']")
                synchronisations = xml_trans[0].findall(
                    ".//label[@kind='synchronisation']")
                for synchronisation in synchronisations:
                    synchronisation_text = "".join(
                        synchronisation.text.split(" "))
                    if synchronisation_text[-1] == "?":
                        # chercher synchronisation[:len(synchronisation)-1] dans les cycles de sync_rp[name]
                        for rnz_name, rnz_template in rnz_copy.items():
                            for rnz_cycle in rnz_template:
                                for rnz_transition in rnz_cycle[1]:
                                    xml_trans_rnz = root.findall(
                                        ".//transition[@id='" + rnz_transition + "']")
                                    synchronisations_rnz = xml_trans_rnz[0].findall(
                                        ".//label[@kind='synchronisation']")
                                    for synchro in synchronisations_rnz:
                                        synchro_text = "".join(
                                            synchro.text.split(" "))
                                        if synchro_text[-1] == "!":
                                            synchro_text = synchro_text.split("[")[
                                                0]
                                            synchronisation_text = synchronisation_text.split("[")[
                                                0]
                                            if synchro_text == synchronisation_text:
                                                if cycle not in rnz_copy[name]:
                                                    rnz_copy[name].append(
                                                        cycle)
    return rnz_copy


def reverse(results, results_nz):
    output = {}
    for name, template in results.items():
        output[name] = []
        for cycle in template:
            if cycle not in results_nz[name]:
                output[name].append(cycle)
    return output


def main(path):
    tree = ET.parse(path)
    root = tree.getroot()
    transitions = root.findall('.//transition')
    templates = root.findall('.//template')
    results = {}
    for template in templates:
        template_name = template.find('name').text
        cycles, G, para = find_cycles(template)
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
            for parallel in para:
                for par in parallel:
                    if par in cycle[1]:
                        idx = cycle[1].index(par)
                        par_idx = parallel.index(par)
                        new_cycle = [cycle[0], cycle[1]
                                     [:idx]+[parallel[1-par_idx]]+cycle[1][idx+1:]]
                        result.append(new_cycle)

        results[template_name] = result
    results_non_zeno = {}
    results_potential_zeno = {}
    for name, template in results.items():
        results_non_zeno[name] = []
        results_potential_zeno[name] = []
        for cycle in template:
            if suffCond(cycle, root):
                results_non_zeno[name].append(cycle)
            else:
                results_potential_zeno[name].append(cycle)

    rnz = syncCond(results_potential_zeno, results_non_zeno, root)
    rz = reverse(results, rnz)

    is_zeno = False
    for template in rz.values():
        if template != []:
            is_zeno = True

    if is_zeno:
        print("Votre système possède un ou plusieurs cycles zeno :")
        print(rz)
    else:
        print("Votre système ne possède aucun cycle zeno.")


if __name__ == "__main__":
    path = 'data/fischer.xml'
    main(path)

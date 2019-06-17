'''
Show the pattern as a tree plot with node attributes and role labels
'''

import pydot
import visualise_spacy_pattern


ROLE_COLOURS = [
    'deeppink1',
    'cyan',
    'dodgerblue',
    'aquamarine',
]

NULL_COLOUR = 'grey'

DEFAULT_SUBGRAPH_ATTRS = {
    'color': 'lightgrey',
    'shape': 'box',
    # 'style': 'rounded',
    'fontname': 'palatino',
    'fontsize': 10,
    'penwidth': 1,
}

DEFAULT_NODE_ATTRS = {
    'color': 'cyan',
    'shape': 'box',
    'style': 'rounded',
    'fontname': 'palatino',
    'fontsize': 10,
    'penwidth': 2
}


def get_label_colour_dict(labels):
    labels = [l for l in labels if l]  # Ignore null labels
    labels = set(labels)
    label2colour = {label: ROLE_COLOURS[i] for i, label in enumerate(labels)}
    return label2colour


def assign_role_colours(graph, token_labels):
    label2colour = get_label_colour_dict(token_labels)
    nodes = graph.get_nodes()
    for node, label in zip(nodes, token_labels):
        if label:
            colour = label2colour[label]
            node.set_color(colour)
        else:
            node.set_color(NULL_COLOUR)
    return graph


def get_nodes_with_label(nodes, labels, with_label):
    nodes_with_label = []
    for node, label in zip(nodes, labels):
        if label == with_label:
            nodes_with_label.append(node)
    return nodes_with_label


def add_role_label_clusters(graph, labels):
    new_graph = pydot.Dot(graph_type='graph')
    nodes = graph.get_nodes()
    for label in set(labels):
        nodes_with_label = get_nodes_with_label(nodes, labels, label)
        if not label:
            for node in nodes_with_label:
                new_graph.add_node(node)
        else:
            subgraph_name = 'cluster_' + label
            subgraph = pydot.Subgraph(graph_name=subgraph_name, **DEFAULT_SUBGRAPH_ATTRS)
            subgraph.set_label(label)
            for node in nodes_with_label:
                subgraph.add_node(node)
            new_graph.add_subgraph(subgraph)
    for edge in graph.get_edges():
        new_graph.add_edge(edge)
    return new_graph


def to_pydot(pattern):
    spacy_dep_pattern = pattern.spacy_dep_pattern
    labels = pattern.token_labels_depth_order
    graph = visualise_spacy_pattern.to_pydot(spacy_dep_pattern)
    graph = assign_role_colours(graph, labels)
    graph = add_role_label_clusters(graph, labels)
    return graph

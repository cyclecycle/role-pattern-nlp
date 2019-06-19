'''
Show the pattern as a tree plot with node attributes and role labels
'''

import pydot
import visualise_spacy_pattern
from role_pattern_nlp import util


ROLE_COLOURS = [
    'deeppink1',
    'cyan',
    'dodgerblue',
    'aquamarine',
]

NULL_COLOUR = 'grey'

DEFAULT_STYLE_ATTRS = {
    'fontname': 'palatino',
    'fontsize': 10,
}

DEFAULT_SUBGRAPH_ATTRS = {
    # 'color': 'grey',
    # 'style': 'solid',
    'penwidth': 1,
}

DEFAULT_NODE_ATTRS = {
    'color': 'cyan',
    'shape': 'box',
    'style': 'rounded',
    'penwidth': 2,
}

LEGEND_ATTRS = {
    'ranksep': 0,
    'penwidth': 0,
}


def get_label_colour_dict(labels):
    labels = [l for l in labels if l]  # Ignore null labels
    labels = util.unique_list(labels)
    label2colour = {label: ROLE_COLOURS[i] for i, label in enumerate(labels)}
    return label2colour


def assign_role_colours(graph, token_labels, label2colour):
    nodes = graph.get_nodes()
    for node, label in zip(nodes, token_labels):
        if label:
            colour = label2colour[label]
            node.set_color(colour)
        else:
            node.set_color(NULL_COLOUR)
    return graph


# def add_legend(graph, label2colour):
#     legend = pydot.Subgraph(graph_name='cluster_legend', **DEFAULT_STYLE_ATTRS, **LEGEND_ATTRS)
#     legend.set_label('Legend')
#     for label, colour in label2colour.items():
#         label_node = pydot.Node(name=label, **LEGEND_NODE_ATTRS)
#         colour_node = pydot.Node(name=colour, fontcolor='white', fontsize=0, **LEGEND_NODE_ATTRS)
#         # colour_node.set_color(colour)
#         edge = pydot.Edge(label_node, colour_node, style='invis', contraint='false')
#         legend.add_node(label_node)
#         legend.add_node(colour_node)
#         legend.add_edge(edge)
#     graph.add_subgraph(legend)
#     return graph


def create_legend(label2colour):
    legend = pydot.Dot(graph_type='graph', **DEFAULT_STYLE_ATTRS)
    legend_cluster = pydot.Subgraph(graph_name='cluster_legend', **DEFAULT_STYLE_ATTRS, **LEGEND_ATTRS)
    legend_cluster.set_label('Role labels')
    rows = []
    for label, colour in label2colour.items():
        row = '<td>{0}</td><td bgcolor="{1}" width="30"></td>'.format(label, colour)
        row = '<tr>{}</tr>'.format(row)
        rows.append(row)
    table = '<<table border="0" cellborder="1" cellspacing="0" cellpadding="4">{}</table>>'.format('\n'.join(rows))
    table = pydot.Node(name='legend_table', label=table, shape='none')
    legend_cluster.add_node(table)
    legend.add_subgraph(legend_cluster)
    return legend


def get_nodes_with_label(nodes, labels, with_label):
    nodes_with_label = []
    for node, label in zip(nodes, labels):
        if label == with_label:
            nodes_with_label.append(node)
    return nodes_with_label


def add_role_label_clusters(graph, labels):
    new_graph = pydot.Dot(graph_type='graph', **DEFAULT_STYLE_ATTRS)
    nodes = graph.get_nodes()
    for label in util.unique_list(labels):
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


def to_pydot(pattern, with_legend=False):
    spacy_dep_pattern = pattern.spacy_dep_pattern
    labels_depth_order = pattern.token_labels_depth_order
    labels_original_order = pattern.token_labels
    graph = visualise_spacy_pattern.to_pydot(spacy_dep_pattern)
    label2colour = get_label_colour_dict(labels_original_order)
    graph = assign_role_colours(graph, labels_depth_order, label2colour)
    if with_legend:
        legend = create_legend(label2colour)
        return graph, legend
    return graph

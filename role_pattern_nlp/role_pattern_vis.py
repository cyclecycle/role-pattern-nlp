'''
Show the pattern as a tree plot with node attributes and role labels
'''

import pydot
from spacy.tokens import Token
import visualise_spacy_tree
import visualise_spacy_pattern
from role_pattern_nlp import util


ROLE_COLOURS = [
    'deeppink1',
    'purple',
    'dodgerblue',
    'cyan',
]

NULL_COLOUR = 'grey'

DEFAULT_COLOUR = 'aquamarine'

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
    'color': DEFAULT_COLOUR,
    'shape': 'box',
    'style': 'rounded',
    'penwidth': 2,
    'margin': 0.25,
    **DEFAULT_STYLE_ATTRS,
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


def create_legend(label2colour):
    legend = pydot.Dot(graph_type='graph', **DEFAULT_STYLE_ATTRS)
    legend_cluster = pydot.Subgraph(graph_name='cluster_legend', **DEFAULT_STYLE_ATTRS, **LEGEND_ATTRS)
    rows = []
    for label, colour in label2colour.items():
        row = '<td>{0}</td><td bgcolor="{1}" width="30"></td>'.format(label, colour)
        row = '<tr>{}</tr>'.format(row)
        rows.append(row)
    row = '<tr><td>Null</td><td bgcolor="{}" width="30"></td></tr>'.format(NULL_COLOUR)
    rows.append(row)
    row = '<tr><td width="100">No label</td><td bgcolor="{}" width="30"></td></tr>'.format(DEFAULT_COLOUR)
    rows.append(row)
    table = '<table border="0" cellborder="1" cellspacing="0" cellpadding="4">{}</table>'.format('\n'.join(rows))
    table = '<font face="{0}" size="{1}">{2}</font>'.format(
        DEFAULT_STYLE_ATTRS['fontname'],
        DEFAULT_STYLE_ATTRS['fontsize'] - 2,
        table,
    )
    html = '<{}>'.format(table)
    html = pydot.Node(name='legend_table', label=html, shape='none')
    legend_cluster.add_node(html)
    legend.add_subgraph(legend_cluster)
    return legend


def nodes_with_label(nodes, labels, with_label):
    nodes_with_label = []
    for node, label in zip(nodes, labels):
        if label == with_label:
            nodes_with_label.append(node)
    return nodes_with_label


def add_role_label_clusters(graph, labels):
    new_graph = pydot.Dot(graph_type='graph', **DEFAULT_STYLE_ATTRS)
    all_nodes = graph.get_nodes()
    for label in util.unique_list(labels):
        nodes = nodes_with_label(all_nodes, labels, label)
        if not label:
            for node in nodes:
                new_graph.add_node(node)
        else:
            subgraph_name = 'cluster_' + label
            subgraph = pydot.Subgraph(graph_name=subgraph_name, **DEFAULT_SUBGRAPH_ATTRS)
            subgraph.set_label(label)
            for node in nodes:
                subgraph.add_node(node)
            new_graph.add_subgraph(subgraph)
    for edge in graph.get_edges():
        new_graph.add_edge(edge)
    return new_graph


def pattern_to_pydot(pattern, legend=False):
    spacy_dep_pattern = pattern.spacy_dep_pattern
    labels_depth_order = pattern.token_labels_depth_order
    labels_original_order = pattern.token_labels
    graph = visualise_spacy_pattern.to_pydot(spacy_dep_pattern)
    for node in graph.get_nodes():
        for k, v in DEFAULT_NODE_ATTRS.items():
            node.set(k, v)
    if pattern.label2colour:
        label2colour = pattern.label2colour
    else:
        label2colour = get_label_colour_dict(labels_original_order)
        pattern.label2colour = label2colour
    graph = assign_role_colours(graph, labels_depth_order, label2colour)
    if legend:
        legend = create_legend(label2colour)
        return graph, legend
    return graph


def match_to_pydot(match, label2colour={}, legend=False):
    labels = match.keys()
    if not label2colour:
        label2colour = get_label_colour_dict(labels)
    doc = util.doc_from_match(match)
    try:
        Token.set_extension('plot', default=DEFAULT_NODE_ATTRS)
    except:
        pass
    for token in doc:
        colour = DEFAULT_COLOUR
        for match_token in match.match_tokens:
            if match_token.i == token.i:
                colour = NULL_COLOUR
            for label, labelled_tokens in match.items():
                if token.i in [t.i for t in labelled_tokens]:
                    colour = label2colour[label]
        token._.plot['color'] = colour
    graph = visualise_spacy_tree.to_pydot(doc)
    for edge in graph.get_edges():
        for k, v in DEFAULT_STYLE_ATTRS.items():
            edge.set(k, v)
    if legend:
        legend = create_legend(label2colour)
        return graph, legend
    return graph

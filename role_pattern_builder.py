from spacy_dependency_pattern_builder import build_spacy_dependency_pattern
from role_pattern import RolePattern
import util
from constants import DEFAULT_BUILD_PATTERN_TOKEN_FEATURE_DICT


class RolePatternBuilder():

    def __init__(self):
        pass

    def build(self, doc, match_example, token_feature_dict=DEFAULT_BUILD_PATTERN_TOKEN_FEATURE_DICT):
        pattern = build_pattern(
            doc,
            match_example,
            token_feature_dict=token_feature_dict
        )
        role_pattern = RolePattern(
            pattern['spacy_dep_pattern'],
            pattern['token_labels']
        )
        return role_pattern


def build_pattern(doc, match_example, token_feature_dict=DEFAULT_BUILD_PATTERN_TOKEN_FEATURE_DICT):
    util.annotate_token_depth(doc)
    nx_graph = util.doc_to_nx_graph(doc)
    tokens = [sublist for _list in match_example.values() for sublist in _list]
    match_tokens = util.smallest_connected_subgraph(tokens, nx_graph, doc)
    token_labels = build_pattern_label_list(match_tokens, match_example)
    spacy_dep_pattern = build_spacy_dependency_pattern(
        doc,
        match_tokens,
        token_feature_dict=token_feature_dict
    )
    pattern = {
        'spacy_dep_pattern': spacy_dep_pattern,
        'token_labels': token_labels
    }
    return pattern


def build_pattern_label_list(match_tokens, match_example):
    match_token_labels = []
    for w in match_tokens:
        label = None
        for label_, tokens in match_example.items():
            if w in tokens:
                label = label_
        match_token_labels.append(label)
    return match_token_labels

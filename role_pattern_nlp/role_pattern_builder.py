from spacy_pattern_builder import build_dependency_pattern
from role_pattern_nlp.role_pattern import RolePattern
import util
from role_pattern_nlp.constants import DEFAULT_BUILD_PATTERN_TOKEN_FEATURE_DICT, DEFAULT_REFINE_PATTERN_FEATURE_COMBINATIONS, DEFAULT_REFINE_PATTERN_FEATURE_DICT


class RolePatternBuilder():

    def __init__(self):
        pass

    def build(self, doc, match_example, feature_dict=DEFAULT_BUILD_PATTERN_TOKEN_FEATURE_DICT):
        pattern = build_pattern(
            doc,
            match_example,
            feature_dict=feature_dict
        )
        role_pattern = RolePattern(
            pattern['spacy_dep_pattern'],
            pattern['token_labels']
        )
        return role_pattern

    def refine(self, doc, pattern, pos_example, neg_examples):
        pattern = refine_pattern(doc, pattern, pos_example, neg_examples)
        return pattern


def build_pattern(doc, match_example, feature_dict=DEFAULT_BUILD_PATTERN_TOKEN_FEATURE_DICT):
    util.annotate_token_depth(doc)
    nx_graph = util.doc_to_nx_graph(doc)
    tokens = [sublist for _list in match_example.values() for sublist in _list]
    match_tokens = util.smallest_connected_subgraph(tokens, nx_graph, doc)
    token_labels = build_pattern_label_list(match_tokens, match_example)
    spacy_dep_pattern = build_dependency_pattern(
        doc,
        match_tokens,
        feature_dict=feature_dict
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


# def dep_pattern_variations_feature_set_level(pattern, feature_combinations=[]):
#     # A pattern for each combination of features
#     variations = []
#     for features in feature_combinations:
#         new_variation = []
#         for spec in pattern:
#             new_pattern = {k: v for k, v in spec['PATTERN'].items() if k in features}
#             new_spec = {'SPEC': spec['SPEC'], 'PATTERN': new_pattern}
#             new_variation.append(new_spec)
#             pprint(new_variation)
#         variations.append(new_variation)
#     return variations


def pattern_variations_feature_set_level(doc, pattern, feature_combinations, feature_dict):
    # A pattern for each combination of features
    spacy_dep_pattern = pattern.spacy_dep_pattern
    variations = []
    for features in feature_combinations:
        new_variation = []
        for spec in spacy_dep_pattern:
            token_idx = int(spec['SPEC']['NODE_NAME'].split('node')[1])
            token = doc[token_idx]
            new_token_attrs = {
                name: getattr(token, feature_dict[name]) for name in features
            }
            new_spec = {'SPEC': spec['SPEC'], 'PATTERN': new_token_attrs}
            new_variation.append(new_spec)
        new_variation = RolePattern(new_variation, pattern.token_labels)
        variations.append(new_variation)
    return variations


def refine_pattern(doc, pattern, pos_example, neg_examples):
    variations = pattern_variations_feature_set_level(
        doc,
        pattern,
        DEFAULT_REFINE_PATTERN_FEATURE_COMBINATIONS,
        DEFAULT_REFINE_PATTERN_FEATURE_DICT
    )
    for pattern_variation in variations:
        matches = pattern_variation.match(doc)
        matches_neg_example = False
        for neg_example in neg_examples:
            if neg_example in matches:
                matches_neg_example = True
        matches_pos_example = pos_example in matches
        if not matches_neg_example and matches_pos_example:
            return pattern_variation

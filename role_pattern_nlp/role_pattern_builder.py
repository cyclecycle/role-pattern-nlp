from spacy_pattern_builder import build_dependency_pattern, yield_pattern_permutations
from role_pattern_nlp.role_pattern import RolePattern
from role_pattern_nlp import util
from role_pattern_nlp.constants import DEFAULT_BUILD_PATTERN_TOKEN_FEATURE_DICT, DEFAULT_REFINE_PATTERN_FEATURE_COMBINATIONS, DEFAULT_REFINE_PATTERN_FEATURE_DICT
from role_pattern_nlp.exceptions import FeaturesNotInFeatureDictError


class RolePatternBuilder():

    def __init__(self, feature_dict):
        self.feature_dict = feature_dict

    def build(self, doc, match_example, features=[]):
        if not features:
            features = self.feature_dict.keys()
        self.validate_features(features)
        feature_dict = {k: v for k, v in self.feature_dict.items() if k in features}
        role_pattern = build_role_pattern(
            doc,
            match_example,
            feature_dict=feature_dict
        )
        role_pattern.builder = self
        return role_pattern

    def refine(self, doc, pattern, pos_example, neg_examples, feature_sets=DEFAULT_REFINE_PATTERN_FEATURE_COMBINATIONS):
        all_features = set(util.flatten_list(feature_sets))
        self.validate_features(all_features)
        # Check that all required features present in spacy_dependency_pattern.
        # If not, build an intermediary pattern with the required features.
        all_features_are_in_pattern = util.features_are_in_role_pattern(all_features, pattern)
        if not all_features_are_in_pattern:
            pattern = self.build(doc, pos_example)  # Uses all the features in the builder's feature_dict
        refined_pattern_variants = yield_refined_pattern_variants(
            doc, pattern, pos_example, neg_examples, feature_sets
        )
        return refined_pattern_variants

    def validate_features(self, features):
        features_not_in_feature_dict = [f for f in features if f not in self.feature_dict]
        if features_not_in_feature_dict:
            raise FeaturesNotInFeatureDictError('RolePatternBuilder received a list of features which includes features that are not present in the feature_dict. Features not present: {}'.format(', '.join(features_not_in_feature_dict)))


def build_role_pattern(doc, match_example, feature_dict=DEFAULT_BUILD_PATTERN_TOKEN_FEATURE_DICT):
    util.annotate_token_depth(doc)
    nx_graph = util.doc_to_nx_graph(doc)
    tokens = [sublist for _list in match_example.values() for sublist in _list]
    tokens = [doc[token.i] for token in tokens]  # Ensure that the tokens have the ._.depth attribute
    match_tokens = util.smallest_connected_subgraph(tokens, nx_graph, doc)
    token_labels = build_pattern_label_list(match_tokens, match_example)
    spacy_dep_pattern = build_dependency_pattern(
        doc,
        match_tokens,
        feature_dict=feature_dict
    )
    role_pattern = RolePattern(spacy_dep_pattern, token_labels)
    return role_pattern


def build_pattern_label_list(match_tokens, match_example):
    match_token_labels = []
    for w in match_tokens:
        label = None
        for label_, tokens in match_example.items():
            if w in tokens:
                label = label_
        match_token_labels.append(label)
    return match_token_labels


def yield_role_pattern_permutations(role_pattern, feature_sets):
    spacy_dependency_pattern = role_pattern.spacy_dep_pattern
    match_token_labels = role_pattern.token_labels
    dependency_pattern_variants = yield_pattern_permutations(
        spacy_dependency_pattern, feature_sets)
    for dependency_pattern_variant in dependency_pattern_variants:
        assert len(dependency_pattern_variant) == len(spacy_dependency_pattern)
        role_pattern_variant = RolePattern(dependency_pattern_variant, match_token_labels)
        yield role_pattern_variant


def yield_refined_pattern_variants(doc, role_pattern, pos_example, neg_examples, feature_sets):
    role_pattern_variants = yield_role_pattern_permutations(role_pattern, feature_sets)
    for role_pattern_variant in role_pattern_variants:
        matches = role_pattern_variant.match(doc)
        neg_example_matches = [m for m in matches if m in neg_examples]
        pattern_matches_neg_example = any(neg_example_matches)
        pattern_matches_pos_example = pos_example in matches
        if not pattern_matches_neg_example and pattern_matches_pos_example:
            yield role_pattern_variant

from pprint import pformat, pprint
import spacy_pattern_builder
from role_pattern_nlp.role_pattern import RolePattern
from role_pattern_nlp import validate
from role_pattern_nlp import util
from role_pattern_nlp.constants import DEFAULT_BUILD_PATTERN_TOKEN_FEATURE_DICT, DEFAULT_REFINE_PATTERN_FEATURE_COMBINATIONS, DEFAULT_REFINE_PATTERN_FEATURE_DICT
from role_pattern_nlp.exceptions import FeaturesNotInFeatureDictError, RolePatternDoesNotMatchExample


class RolePatternBuilder():

    def __init__(self, feature_dict):
        self.feature_dict = feature_dict

    def build(self, match_example, features=[], **kwargs):
        if not features:
            features = self.feature_dict.keys()
        self.validate_features(features)
        feature_dict = {k: v for k, v in self.feature_dict.items() if k in features}
        role_pattern = build_role_pattern(
            match_example,
            feature_dict=feature_dict,
            **kwargs,
        )
        role_pattern.builder = self
        return role_pattern

    def refine(self, pattern, pos_example, neg_examples, feature_sets=DEFAULT_REFINE_PATTERN_FEATURE_COMBINATIONS):
        all_features = set(util.flatten_list(feature_sets))
        self.validate_features(all_features)
        # Check that all required features present in spacy_dependency_pattern.
        # If not, build an intermediary pattern with the required features.
        all_features_are_in_pattern = validate.features_are_in_role_pattern(all_features, pattern)
        if not all_features_are_in_pattern:
            pattern = self.build(pos_example)  # Uses all the features in the builder's feature_dict
        refined_pattern_variants = yield_refined_pattern_variants(
            pattern, pos_example, neg_examples, feature_sets
        )
        return refined_pattern_variants

    def validate_features(self, features):
        features_not_in_feature_dict = [f for f in features if f not in self.feature_dict]
        if features_not_in_feature_dict:
            raise FeaturesNotInFeatureDictError('RolePatternBuilder received a list of features which includes features that are not present in the feature_dict. Features not present: {}'.format(', '.join(features_not_in_feature_dict)))


def build_role_pattern(match_example, feature_dict=DEFAULT_BUILD_PATTERN_TOKEN_FEATURE_DICT, validate_pattern=True):
    doc = util.doc_from_match(match_example)
    util.annotate_token_depth(doc)
    tokens = util.flatten_list(match_example.values())
    tokens = [doc[idx] for idx in util.token_idxs(tokens)]  # Ensure that tokens have the newly added depth attribute
    nx_graph = util.doc_to_nx_graph(doc)
    match_tokens = util.smallest_connected_subgraph(tokens, nx_graph, doc)
    spacy_dep_pattern = spacy_pattern_builder.build_dependency_pattern(
        doc,
        match_tokens,
        feature_dict=feature_dict,
    )
    token_labels = build_pattern_label_list(match_tokens, match_example)
    role_pattern = RolePattern(spacy_dep_pattern, token_labels)
    match_tokens_depth_order = spacy_pattern_builder.util.sort_by_depth(match_tokens)  # Should be same order as the dependency pattern
    token_labels_depth_order = build_pattern_label_list(match_tokens_depth_order, match_example)
    role_pattern.token_labels_depth_order = token_labels_depth_order
    if validate_pattern:
        pattern_does_match_example, matches = validate.pattern_matches_example(role_pattern, match_example)
        if not pattern_does_match_example:
            spacy_dep_pattern = role_pattern.spacy_dep_pattern
            message = [
                'Unable to match example: \n{}'.format(pformat(match_example)),
                'From doc: {}'.format(doc),
                'Constructed role pattern: \n',
                'spacy_dep_pattern: \n{}'.format(pformat(spacy_dep_pattern)),
                'token_labels: \n{}'.format(pformat(role_pattern.token_labels_depth_order)),
            ]
            if matches:
                message.append('Matches found:')
                for match in matches:
                    message += [
                        'Match tokens: \n{}'.format(pformat(match.match_tokens)),
                        'Slots: \n{}'.format(pformat(match)),
                    ]
            else:
                message.append('Matches found: None')
            message = '\n{}'.format('\n'.join(message))
            raise RolePatternDoesNotMatchExample(message)
    return role_pattern


def build_pattern_label_list(match_tokens, match_example):
    match_token_labels = []
    for w in match_tokens:
        label = None
        for label_, tokens in match_example.items():
            token_idxs = [t.i for t in tokens]
            if w.i in token_idxs:  # Use idxs to prevent false inequality caused by state changes
                label = label_
        match_token_labels.append(label)
    return match_token_labels


def yield_role_pattern_permutations(role_pattern, feature_sets):
    spacy_dependency_pattern = role_pattern.spacy_dep_pattern
    match_token_labels = role_pattern.token_labels
    dependency_pattern_variants = spacy_pattern_builder.yield_pattern_permutations(
        spacy_dependency_pattern, feature_sets)
    for dependency_pattern_variant in dependency_pattern_variants:
        assert len(dependency_pattern_variant) == len(spacy_dependency_pattern)
        role_pattern_variant = RolePattern(dependency_pattern_variant, match_token_labels)
        yield role_pattern_variant


def yield_refined_pattern_variants(role_pattern, pos_example, neg_examples, feature_sets):
    pos_example_doc = util.doc_from_match(pos_example)
    role_pattern_variants = yield_role_pattern_permutations(role_pattern, feature_sets)
    for role_pattern_variant in role_pattern_variants:
        matches = role_pattern_variant.match(pos_example_doc)
        pattern_matches_pos_example = pos_example in matches
        neg_example_matches = []
        for neg_example in neg_examples:
            doc = util.doc_from_match(neg_example)
            matches = role_pattern_variant.match(doc)
            if neg_example in matches:
                neg_example_matches.append(neg_example)
        pattern_matches_neg_examples = bool(neg_example_matches)
        if not pattern_matches_neg_examples and pattern_matches_pos_example:
            yield role_pattern_variant

from pprint import pformat, pprint
import itertools
import spacy_pattern_builder
from role_pattern_nlp.role_pattern import RolePattern
from role_pattern_nlp import mutate
from role_pattern_nlp import validate
from role_pattern_nlp import util
from role_pattern_nlp.constants import (
    DEFAULT_BUILD_PATTERN_TOKEN_FEATURE_DICT,
    DEFAULT_REFINE_PATTERN_FEATURE_COMBINATIONS,
    DEFAULT_REFINE_PATTERN_FEATURE_DICT,
)
from role_pattern_nlp.exceptions import (
    FeaturesNotInFeatureDictError,
    RolePatternDoesNotMatchExample,
)


class RolePatternBuilder:
    def __init__(self, feature_dict):
        self.feature_dict = feature_dict

    def build(self, match_example, features=[], **kwargs):
        if not features:
            features = self.feature_dict.keys()
        self.validate_features(features)
        feature_dict = {k: v for k, v in self.feature_dict.items() if k in features}
        role_pattern = build_role_pattern(
            match_example, feature_dict=feature_dict, **kwargs
        )
        role_pattern.builder = self
        return role_pattern

    def refine(
        self,
        pattern,
        pos_matches,
        neg_matches,
        feature_dicts=[DEFAULT_BUILD_PATTERN_TOKEN_FEATURE_DICT],
        fitness_func=mutate.pattern_fitness,
        tree_extension_depth=2,
    ):
        training_match = pos_matches[0]  # Take first pos_match as blue print
        all_matches = pos_matches + neg_matches
        docs = [util.doc_from_match(match) for match in all_matches]
        docs = util.unique_list(docs)
        new_pattern_feature_dict = feature_dicts[0]

        def get_matches(pattern):
            matches = [pattern.match(d) for d in docs]
            matches = util.flatten_list(matches)
            return matches

        def get_fitnesses(patterns, pos_matches, neg_matches):
            matches = [get_matches(variant) for variant in patterns]
            fitnesses = [
                fitness_func(variant, matches, pos_matches, neg_matches)
                for variant, matches in zip(patterns, matches)
            ]
            return fitnesses

        def get_best_fitness_score(fitnesses):
            best_fitness_score = max([fitness['score'] for fitness in fitnesses])
            return best_fitness_score

        def get_node_level_variants(patterns):
            pattern_variants = [
                mutate.yield_node_level_pattern_variants(
                    variant, variant.training_match, feature_dicts
                )
                for variant in patterns
            ]
            pattern_variants = util.flatten_list(pattern_variants)
            return pattern_variants

        def get_tree_level_variants(patterns):
            pattern_variants = [
                mutate.yield_tree_level_pattern_variants(
                    variant, variant.training_match, new_pattern_feature_dict
                )
                for variant in patterns
            ]
            pattern_variants = util.flatten_list(pattern_variants)
            return pattern_variants

        def get_best_variants(variants, fitnesses, best_fitness_score):
            best_variants = [
                variant
                for variant, fitness in zip(pattern_variants, fitnesses)
                if fitness['score'] == best_fitness_score
            ]
            return best_variants

        def get_shortest_variants(variants):
            shortest_length = min(
                [len(variant.spacy_dep_pattern) for variant in variants]
            )
            shortest_variants = [
                variant
                for variant in variants
                if len(variant.spacy_dep_pattern) == shortest_length
            ]
            return shortest_variants

        def remove_duplicates(variants):
            unique_variants = []
            dep_patterns_already = []
            for variant in variants:
                if variant.spacy_dep_pattern not in dep_patterns_already:
                    unique_variants.append(variant)
                dep_patterns_already.append(variant.spacy_dep_pattern)
            return unique_variants

        pattern.training_match = training_match
        pattern_variants = [pattern]

        for i in range(tree_extension_depth):
            pattern_variants += get_tree_level_variants(pattern_variants)

        pattern_variants = remove_duplicates(pattern_variants)
        fitnesses = get_fitnesses(pattern_variants, pos_matches, neg_matches)

        best_fitness_score = get_best_fitness_score(fitnesses)

        if best_fitness_score == 1.0:
            pattern_variants = get_best_variants(
                pattern_variants, fitnesses, best_fitness_score
            )
            pattern_variants = get_shortest_variants(pattern_variants)
            return pattern_variants

        pattern_variants = get_node_level_variants(pattern_variants)
        fitnesses = get_fitnesses(pattern_variants, pos_matches, neg_matches)
        best_fitness_score = get_best_fitness_score(fitnesses)

        # util.interactive_pattern_evaluation(
        #     pattern_variants, fitnesses, fitness_floor=0
        # )

        pattern_variants = get_best_variants(
            pattern_variants, fitnesses, best_fitness_score
        )
        pattern_variants = get_shortest_variants(pattern_variants)

        return pattern_variants

    def validate_features(self, features):
        features_not_in_feature_dict = [
            f for f in features if f not in self.feature_dict
        ]
        if features_not_in_feature_dict:
            raise FeaturesNotInFeatureDictError(
                'RolePatternBuilder received a list of features which includes features that are not present in the feature_dict. Features not present: {}'.format(
                    ', '.join(features_not_in_feature_dict)
                )
            )


def build_role_pattern(
    match_example,
    feature_dict=DEFAULT_BUILD_PATTERN_TOKEN_FEATURE_DICT,
    validate_pattern=True,
):
    doc = util.doc_from_match(match_example)
    util.annotate_token_depth(doc)
    tokens = util.flatten_list(match_example.values())
    tokens = [
        doc[idx] for idx in util.token_idxs(tokens)
    ]  # Ensure that tokens have the newly added depth attribute
    nx_graph = util.doc_to_nx_graph(doc)
    match_tokens = util.smallest_connected_subgraph(tokens, nx_graph, doc)
    spacy_dep_pattern = spacy_pattern_builder.build_dependency_pattern(
        doc, match_tokens, feature_dict=feature_dict
    )
    token_labels = build_pattern_label_list(match_tokens, match_example)
    role_pattern = RolePattern(spacy_dep_pattern, token_labels)
    match_tokens_depth_order = spacy_pattern_builder.util.sort_by_depth(
        match_tokens
    )  # Should be same order as the dependency pattern
    token_labels_depth_order = build_pattern_label_list(
        match_tokens_depth_order, match_example
    )
    role_pattern.token_labels_depth_order = token_labels_depth_order
    if validate_pattern:
        pattern_does_match_example, matches = validate.pattern_matches_example(
            role_pattern, match_example
        )
        if not pattern_does_match_example:
            spacy_dep_pattern = role_pattern.spacy_dep_pattern
            message = [
                'Unable to match example: \n{}'.format(pformat(match_example)),
                'From doc: {}'.format(doc),
                'Constructed role pattern: \n',
                'spacy_dep_pattern: \n{}'.format(pformat(spacy_dep_pattern)),
                'token_labels: \n{}'.format(
                    pformat(role_pattern.token_labels_depth_order)
                ),
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
    match_tokens = sorted(match_tokens, key=lambda t: t.i)
    match_token_labels = []
    for w in match_tokens:
        label = None
        for label_, tokens in match_example.items():
            token_idxs = [t.i for t in tokens]
            if (
                w.i in token_idxs
            ):  # Use idxs to prevent false inequality caused by state changes
                label = label_
        match_token_labels.append(label)
    return match_token_labels

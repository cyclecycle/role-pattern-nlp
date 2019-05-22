from spacy.matcher import DependencyTreeMatcher
from spacy_dependency_pattern_builder import build_spacy_dependency_pattern
import util


class RolePattern():

    def __init__(self, spacy_dep_pattern, token_labels):
        self.spacy_dep_pattern = spacy_dep_pattern
        self.token_labels = token_labels

    def match(self, doc):
        pattern = {'spacy_dep_pattern': self.spacy_dep_pattern, 'token_labels': self.token_labels}
        matches = find_matches(doc, pattern, 'pattern')
        return matches


def build_matcher(vocab, pattern_dict):
    matcher = DependencyTreeMatcher(vocab)
    for name, pattern in pattern_dict.items():
        dep_pattern = pattern['spacy_dep_pattern']
        matcher.add(name, None, dep_pattern)
    return matcher

# def build_matcher(vocab, spacy_dep_pattern):
#     matcher = DependencyTreeMatcher(vocab)
#     matcher.add('pattern', None, spacy_dep_pattern)
#     return matcher


def find_matches(doc, pattern, pattern_name='pattern'):
    matcher = build_matcher(doc.vocab, {pattern_name: pattern})
    matches = matcher(doc)
    labels = pattern['token_labels']
    match_list = []
    for match_id, token_idxs in matches:
        pattern_name = matcher.vocab.strings[match_id]
        tokens = [doc[idx] for idx in token_idxs]
        tokens = sorted(tokens, key=lambda t: t.i)
        match_item = {label: [] for label in pattern['token_labels'] if label}
        for label, token in zip(labels, tokens):
            if label:
                match_item[label].append(token)
        match_list.append(match_item)
    return match_list


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


def pattern_variations_feature_set_level(doc, pattern, feature_combinations, token_feature_dict):
    # A pattern for each combination of features
    spacy_dep_pattern = pattern['spacy_dep_pattern']
    variations = []
    for features in feature_combinations:
        new_variation = []
        for spec in spacy_dep_pattern:
            token_idx = int(spec['SPEC']['NODE_NAME'])
            token = doc[token_idx]
            new_token_attrs = {
                name: getattr(token, token_feature_dict[name]) for name in features
            }
            new_spec = {'SPEC': spec['SPEC'], 'PATTERN': new_token_attrs}
            new_variation.append(new_spec)
        new_variation = {
            'spacy_dep_pattern': new_variation,
            'labels': pattern['labels']
        }
        variations.append(new_variation)
    return variations


# def refine_pattern(doc, pattern, pos_example, neg_examples):
#     variations = pattern_variations_feature_set_level(
#         doc,
#         pattern,
#         DEFAULT_REFINE_PATTERN_FEATURE_COMBINATIONS,
#         DEFAULT_REFINE_PATTERN_FEATURE_DICT
#     )
#     # print(len(variations))
#     # successful_patterns = []
#     for pattern_variation in variations:
#         # pprint(new_pattern)
#         matches = find_matches(doc, pattern_variation)
#         matches_neg_example = False
#         for neg_example in neg_examples:
#             if neg_example in matches:
#                 matches_neg_example = True
#         matches_pos_example = pos_example in matches
#         if not matches_neg_example and matches_pos_example:
#             # successful_patterns.append(pattern_variation)
#             return pattern_variation
#     # return successful_patterns
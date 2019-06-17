from role_pattern_nlp import util


def features_are_in_dependency_pattern(features, pattern):
    for pattern_element in pattern:
        for feature in features:
            if feature not in pattern_element['PATTERN']:
                return False
    return True


def features_are_in_role_pattern(features, role_pattern):
    spacy_dependency_pattern = role_pattern.spacy_dep_pattern
    return features_are_in_dependency_pattern(features, spacy_dependency_pattern)


def pattern_matches_example(role_pattern, match_example):
    doc = util.doc_from_match(match_example)
    matches = role_pattern.match(doc)
    if match_example in matches:
        return True
    return False

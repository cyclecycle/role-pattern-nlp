from role_pattern_nlp import util
from role_pattern_nlp import match
from role_pattern_nlp import role_pattern_vis


class RolePattern():

    def __init__(self, spacy_dep_pattern, token_labels):
        self.spacy_dep_pattern = spacy_dep_pattern
        self.token_labels = token_labels
        self.token_labels_depth_order = None  # Corresponds one-to-one with spacy_dep_pattern
        self.name = 'pattern'
        self.builder = None
        self.label2colour = {}  # For visualisation

    def match(self, doc):
        pattern = {'spacy_dep_pattern': self.spacy_dep_pattern, 'token_labels': self.token_labels}
        matches = match.find_matches(doc, pattern, 'pattern')
        return matches

    def to_pydot(self, **kwargs):
        return role_pattern_vis.pattern_to_pydot(self, **kwargs)

    def match_to_pydot(self, match, **kwargs):
        return role_pattern_vis.match_to_pydot(self, match, **kwargs)

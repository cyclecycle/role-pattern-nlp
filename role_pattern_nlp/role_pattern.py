from role_pattern_nlp import util
from role_pattern_nlp import match
from role_pattern_nlp import role_pattern_vis


class RolePattern():

    def __init__(self, spacy_dep_pattern, token_labels):
        self.spacy_dep_pattern = spacy_dep_pattern
        self.token_labels = token_labels
        self.token_labels_depth_order = None  # Match one to one with spacy_dep_pattern
        self.name = 'pattern'
        self.builder = None

    def match(self, doc):
        pattern = {'spacy_dep_pattern': self.spacy_dep_pattern, 'token_labels': self.token_labels}
        matches = match.find_matches(doc, pattern, 'pattern')
        return matches

    def to_pydot(self):
        return role_pattern_vis.to_pydot(self)

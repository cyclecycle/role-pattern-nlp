from role_pattern_nlp import util


class RolePattern():

    def __init__(self, spacy_dep_pattern, token_labels):
        self.spacy_dep_pattern = spacy_dep_pattern
        self.token_labels = token_labels
        self.name = 'pattern'
        self.builder = None

    def match(self, doc):
        pattern = {'spacy_dep_pattern': self.spacy_dep_pattern, 'token_labels': self.token_labels}
        matches = util.find_matches(doc, pattern, 'pattern')
        return matches

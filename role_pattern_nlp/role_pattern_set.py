class RolePatternSet():

    def __init__(self, patterns=None):
        if patterns:
            self.patterns = patterns
        else:
            self.patterns = []

    def __iter__(self):
        pass

    def add(self, pattern):
        self.patterns.append(pattern)

    def match(self, doc):
        # Build matcher from all patterns
        pass

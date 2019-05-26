# Role Pattern

Build and match linguistic patterns for role labelling. Provides a example-driven approach to generate and refine patterns.

Uses graph-based pattern matching, built on SpaCy.

## Example

```python
# First, parse a string to create a SpaCy Doc object
import en_core_web_sm
text = "Forging involves the shaping of metal using localized compressive forces."
nlp = en_core_web_sm.load()
doc = nlp(text)

from role_pattern_nlp import RolePatternBuilder

# Provide an example by mapping role labels to tokens
match_example = {
    'arg1': [doc[0]],  # [Forging]
    'pred': [doc[1]],  # [involves]
    'arg2': [doc[3]],  # [shaping]
}

''' Create a dictionary of all the features we want the RolePatternBuilder to have access to
when building and refining patterns '''
feature_dict = {'DEP': 'dep_', 'TAG': 'tag_'}

# Instantiate the pattern builder
role_pattern_builder = RolePatternBuilder(feature_dict)

#  Build a pattern. It will use all the features in the feature_dict by default
role_pattern = role_pattern_builder.build(doc, match_example)  

# Match against any doc with the role_pattern
matches = role_pattern.match(doc)
print(matches)
'''
[{'arg1': [Forging], 'arg2': [shaping], 'pred': [involves]}]
'''
```

## Built with

- [SpaCy](https://spacy.io) - DependencyMatcher
- [SpaCy pattern builder](https://github.com/cyclecycle/spacy-pattern-builder)
- [networkx](https://github.com/networkx/networkx) - Used by SpaCy pattern builder
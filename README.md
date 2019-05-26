# role-pattern

Build and match linguistic patterns for role labelling using a data-driven approach to generate and refine patterns.

This approach uses graph-based pattern matching, built on SpaCy. Patterns are generated using spacy-pattern-builder.

## Example

```python
import en_core_web_sm
text = "Forging involves the shaping of metal using localized compressive forces."
nlp = en_core_web_sm.load()
doc = nlp(text)

from role_pattern_nlp import RolePatternBuilder

match_example = {
    'arg1': [doc[0]],  # [Forging]
    'pred': [doc[1]],  # [involves]
    'arg2': [doc[3]],  # [shaping]
}

# Create a dictionary of all the features we want our RolePatternBuilder to have access to
feature_dict = {'DEP': 'dep_', 'TAG': 'tag_'}
role_pattern_builder = RolePatternBuilder(feature_dict)  # Instantiate the pattern builder
pattern = role_pattern_builder.build(doc, match_example)  #  Build a pattern. It will use all the features in the feature_dict by default.
print(pattern)

matches = pattern.match(doc)
print(matches)
'''
[{'arg1': [Forging], 'arg2': [shaping], 'pred': [involves]}]
'''
```

## Built with

- Spacy - DependencyMatcher
- Spacy pattern builder
- networkx
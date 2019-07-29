from role_pattern_nlp import util
from test.test_role_pattern import doc3


idxs_to_tokens = util.idxs_to_tokens

cases = [
    {
        'doc': doc3,
        'with_tokens': idxs_to_tokens(doc3, [2, 8]),
        'expected': idxs_to_tokens(doc3, [2, 4, 8]),
    }
]


def test_smallest_connect_subgraph():
    for case in cases:
        doc = case['doc']
        with_tokens = case['with_tokens']
        expected = case['expected']
        nx_graph = util.doc_to_nx_graph(doc)
        connected_tokens = util.smallest_connected_subgraph(with_tokens, nx_graph, doc)
        assert connected_tokens == expected

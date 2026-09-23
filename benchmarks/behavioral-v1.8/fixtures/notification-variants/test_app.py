from selector import reachable_variants


def test_normal_has_variants():
    assert len(reachable_variants("NORMAL")) >= 2

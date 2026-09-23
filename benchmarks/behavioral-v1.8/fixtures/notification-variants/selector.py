from catalogue import STATE_VARIANTS


def reachable_variants(state: str):
    return STATE_VARIANTS[state][:2]

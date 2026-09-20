
def clean_and_flatten_scores(raw_batches: list[list[int | None]]) -> list[int]:

    cleanL: list[int] = []

    for oL in raw_batches:
        for n in oL:
            if n:
                if n <
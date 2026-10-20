"""Checkpoints compared in the project.

All are binary SST-2 sentiment classifiers so they share a label space.
`params_m` (millions of parameters, approximate) is used by the size analysis.

!! VERIFY BEFORE THE FIRST RUN !!
Checkpoint names are written from memory and were NOT checked against
huggingface.co (no network access when this was written). The *-large entries
are the least certain: search the Hub for SST-2 fine-tunes of bert-large and
roberta-large and confirm what each was trained on. If you cannot find large
checkpoints trained on the same data as the base ones, the cleanest fix is to
fine-tune all five models yourself on SST-2 with one shared recipe, so the only
thing that differs between models is the architecture/size.
"""

MODELS = {
    "distilbert":    {"checkpoint": "distilbert-base-uncased-finetuned-sst-2-english", "pos_index": 1, "params_m": 66},
    "bert":          {"checkpoint": "textattack/bert-base-uncased-SST-2",              "pos_index": 1, "params_m": 110},
    "roberta":       {"checkpoint": "textattack/roberta-base-SST-2",                   "pos_index": 1, "params_m": 125},
    "bert-large":    {"checkpoint": "assemblyai/bert-large-uncased-sst2",              "pos_index": 1, "params_m": 340},   # VERIFY
    "roberta-large": {"checkpoint": "philschmid/roberta-large-sst2",                   "pos_index": 1, "params_m": 355},   # VERIFY
}

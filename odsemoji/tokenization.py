from ufal.udpipe import Model, Pipeline, ProcessingError # pylint: disable=no-name-in-module
import tqdm


def get_model(modelfile='/media/data/word2vec/ufal/udpipe-ud-2.0-170801/russian-syntagrus-ud-2.0-170801.udpipe'):
    return Model.load(modelfile)


def get_pipeline(model):
    return Pipeline(model, 'tokenize', Pipeline.DEFAULT, Pipeline.DEFAULT, 'conllu')

def text2tagged(lines):
    model = get_model()
    pipeline = get_pipeline(model)
    processed_lines = []
    for line in tqdm.tqdm(lines):
        processed = pipeline.process(line)
        output = [l for l in processed.split('\n') if not l.startswith('#')]
        print([w.split('\t') for w in output if w and (w[3] not in ['PUNCT'])])
        tagged = ['_'.join(w.split('\t')[2:4]) for w in output if w and (w.split('\t')[3] not in ['PUNCT'])]
        processed_lines.append(tagged)
    return processed_lines

from ufal.udpipe import Model, Pipeline, ProcessingError # pylint: disable=no-name-in-module
import tqdm

def get_pipeline(modelfile='/media/data/word2vec/ufal/udpipe-ud-2.0-170801/russian-syntagrus-ud-2.0-170801.udpipe'):
    model = Model.load(modelfile)
    pipeline = Pipeline(model, 'tokenize', Pipeline.DEFAULT, Pipeline.DEFAULT, 'conllu')
    return pipeline

def text2tagged(lines):
    pipeline = get_pipeline()
    processed_lines = []
    for line in tqdm.tqdm(lines):
        processed = pipeline.process(line)
        output = [l for l in processed.split('\n') if not l.startswith('#')]
        tagged = ['_'.join(w.split('\t')[2:4]) for w in output if w]
        processed_lines.append(tagged)
    return processed_lines

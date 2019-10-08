from onconlp.classification.tnm import TNM

def process_document(text):
    return [process_sentence(s) for s in split_sentences(text)]
        
def process_sentence(text):
    return [TNM(), TNM()]

def split_sentences(text):
    return []




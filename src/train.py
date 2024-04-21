import spacy

nlp = spacy.load('en_core_web_lg')
ner = nlp.get_pipe('ner')

doc=nlp("Nithin Joseph is the president of the USA.")
print(doc.ents)
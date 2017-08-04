import gensim
import re

file =  open("states", 'r', encoding='utf8')
states = []
for line in file:
	states.append(line.replace("\n","").lower())
file.close()

model = gensim.models.Word2Vec.load("D:\WikiCorpus\WikiModel\wiki.en.word2vec.model")
states = [term for term in states if term in model.wv.vocab]

statesSimilarDict = {}
for state in states:
	print(state)
	similars = model.most_similar(positive=[state],topn=20)
	statesSimilarDict[state] = similars


r = re.compile(r"\'(.+?)\'")
matches = list(set(re.findall(r, str(statesSimilarDict))))
matches.sort()
matchesSet = []
for match in matches:
	r = re.compile(r"[\u3400-\u9FFF]+?")
	if not re.match(r, match):
		matchesSet.append(match)

file = open("stateSimilars", 'w', encoding='utf8')
for state in matchesSet:
	file.write(state+ "\n")
file.close()

# from preprocessing import preprocessing
# import re



# file = open("comapnyEmbedding\China Finance Online Co. (ADR) product",'r', encoding='utf8')

# original = file.read()
# processed = preprocessing(original)
# file.close()

# file = open("processingTest\original", 'w', encoding='utf8')
# file.write(original)
# file.close()

# file = open("processingTest\processed", 'w', encoding='utf8')
# file.write(processed)
# file.close()



from os import listdir
import pandas as pd
import string

# companies = []
# for file in files:
# 	openfile = file
# 	df_comps = pd.read_csv("labelData/" + openfile, index_col=None, header=None)
# 	companies.extend(list(df_comps[0]))

# print(len(companies))
# print(len(set(companies)))


files = listdir("labelData")
files = [file for file in files if "csv" in file]
a = []
for file in files:
    df_comps = pd.read_csv("labelData/" + file, index_col=None, header=None)

    companyTupleList = []
    def buildTupleList(row):
        companyTuple = (row[0], row[1])
        companyTupleList.append(companyTuple)

    df_comps.apply(buildTupleList, axis=1)

    for company, related in companyTupleList:
        companyDict = {}
        companyDict['name'] = company
        companyDict['query'] = "{} product".format(company)
        companyDict['related'] = related

        exclude = set(string.punctuation)
        companyName = ''.join(p for p in company if p not in exclude)
        companyName = companyName.replace(" ", "_").lower()  ##Build self.companyName
        companyDict['filename'] = companyName

        companyDict['targetCompany'] = file
        a.append(companyDict)
print(a[0])
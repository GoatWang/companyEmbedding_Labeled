mkdir index

IndriBuildIndex indexBuilder.param
dumpindex index/company stats > Stats/stats

IndriBuildIndex ProcessedIndexBuilder.param
dumpindex index/processedCompany stats > Stats/processedstats


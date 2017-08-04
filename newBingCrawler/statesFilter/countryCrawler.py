import requests
from bs4 import BeautifulSoup

headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'}
re = requests.get("https://www.state.gov/misc/list/", headers=headers)
soup = BeautifulSoup(re.text, 'lxml')
As = soup.select(".no-bullet a")

print(len(As))
file = open('states', 'w', encoding='utf8')
for a in As:
	if 'www.state.gov' in str(a):
		file.write(a.text+"\n")
file.close()
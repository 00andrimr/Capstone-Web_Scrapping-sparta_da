from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

#insert the scrapping here
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

url_get = requests.get('https://www.coingecko.com/en/coins/ethereum/historical_data?start_date=2020-01-01&end_date=2021-06-30#panel',headers=headers)
soup = BeautifulSoup(url_get.content,"html.parser")

#find your right key here
t_headers = soup.find('table').find('thead').find_all('th')
t_temps = soup.find('table').find('tbody').find_all('tr')

header = []
temp = []

#looping header table
for t_header in t_headers:
    th_text = str(t_header.text).strip()
    header.append(th_text)

#looping row table
for t_temp in t_temps:
    th = t_temp.select_one('th') # if inspect from website date using th element this use to get date
    td = t_temp.findAll('td') # get td child of row as array

    td_text_date = str(th.text).strip()
    td_market_cap = str(td[0].text).strip()
    td_volume = str(td[1].text).strip()
    td_open = str(td[2].text).strip()
    td_close = str(td[3].text).strip()
    td_tuple = (td_text_date, td_market_cap, td_volume, td_open, td_close) # create tuple

    temp.append(td_tuple)

temp

#change into dataframe
df = pd.DataFrame(temp, columns = ('td_text_date','td_market_cap','td_volume','td_open','td_close'))
df = df[['td_text_date','td_volume']]
df = df.rename({'td_text_date': 'Date', 'td_volume': 'Volume'}, axis=1) 
df = df.sort_values(by='Date',ascending=True)
df = df.set_index('Date')

df['Volume'] = df['Volume'].str.replace("$","")
df['Volume'] = df['Volume'].str.replace(",","")
df['Volume'] = df['Volume'].astype('float64')

@app.route("/")
def index(): 
	
	card_data = f'{df["Volume"].mean().round(2)}' #be careful with the " and ' 

	# generate plot
	ax = df.plot(figsize = (20,9)) 
	
	# Rendering plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result = str(figdata_png)[2:-1]

	# render to html
	return render_template('index.html',
		card_data = card_data, 
		plot_result=plot_result
		)


if __name__ == "__main__": 
    app.run(debug=True)
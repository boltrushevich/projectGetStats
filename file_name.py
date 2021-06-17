import pandas as pd
from bs4 import BeautifulSoup

class Naming():

    def __init__(self, file):
        self.file = file
        self.df = pd.read_html(file)[1]
        self.df.columns = ['name', 'value']
        with open(file, 'r') as text:
            self.html_text = text.read()

    def instrument(self):

        instrument = str(self.df.loc[self.df['name'] == 'defaultInstrument']['value'].values[0])

        return instrument

    def strategy(self):

        strategy = 0
        list_of_tags = ['tag', '_tag', '_tag_zero', 'tag_zero', 'algo_comment', '_algo_comment', 'algo_tag',
                        '_algo_tag']

        soup = BeautifulSoup(self.html_text, "lxml")
        soup_str = str(soup.text).split('\n')

        for i in soup_str:
            for j in list_of_tags:
                if j in i:
                    strategy = str(self.df.loc[self.df['name'] == j]['value'].values)

        return strategy

    def direction(self):
        return str(f'{self.strategy()}/{self.instrument()}.json')




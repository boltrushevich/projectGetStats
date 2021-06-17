import pandas as pd
# import os
from bs4 import BeautifulSoup
import json

class Parcer():

    def __init__(self, file):
        self.file = file
        self.df = pd.read_html(file)
        with open(file, 'r') as text:
            self.html_text = text.read()

    def header(self):

        soup = BeautifulSoup(self.html_text, "lxml")
        header = str(soup.find_all('h1', {}))

        strategy = header[5:header.find(' strategy')]
        instrument_s = header[(len(strategy) + 26):header.find(' instrument(s)')]
        window_start = header[(len(strategy) + len(instrument_s) + 46):header.find(' to ')]
        window_end = header[(len(strategy) + len(instrument_s) + len(window_start) + 50):-6]

        header_dict = {
            'name': ['strategy', 'instrument(s)', 'window start', 'window end'],
            'value': [strategy, instrument_s, window_start, window_end],
        }

        header = pd.DataFrame(header_dict)
        header.set_index('name', inplace=True)

        return header

    def account_info(self):
        account_info = self.df[0]
        account_info.columns = ['name', 'value']
        account_info.set_index('name', inplace=True)
        return account_info

    def parameters(self):
        parameters = self.df[1]
        parameters.columns = ['name', 'value']
        parameters.set_index('name', inplace=True)
        return parameters

    def first_for_six(self):
        defaultInstrument_dict = self.df[2].iloc[[0, 3, 7, 8], [0, 1]]
        defaultInstrument_dict.columns = ['name', 'value']
        first_instrument = pd.DataFrame(defaultInstrument_dict)
        first_instrument.set_index('name', inplace=True)
        return first_instrument

    def second_for_six(self):
        secondInstrument_dict = {
            'name': ['First tick time', 'Last tick time', 'Closed positions', 'Orders total'],
            'value': [0, 0, 0, 0],
        }
        second_instrument = pd.DataFrame(secondInstrument_dict)
        second_instrument.set_index('name', inplace=True)
        return second_instrument

    def first_for_nine(self):

        defaultInstrument = 0

        defaultInstrument_dict = {
            'name': ['First tick time', 'Last tick time', 'Closed positions', 'Orders total'],
            'value': [0, 0, 0, 0],
        }

        soup = BeautifulSoup(self.html_text, "lxml")
        soup_str = str(soup.text).split('\n')

        for tr in soup.find_all('tr'):
            if 'defaultInstrument' in tr.text:
                defaultInstrument = str('Instrument ' + tr.text[17:])

        for i in soup_str:
            if defaultInstrument in i:
                first_tick_time_1 = (soup_str[soup_str.index(i) + 1][15:])
                last_tick_time_1 = (soup_str[soup_str.index(i) + 4][14:])
                closed_positions_1 = (soup_str[soup_str.index(i) + 8][16:])
                orders_total_1 = (soup_str[soup_str.index(i) + 9][12:])
                defaultInstrument_dict = {
                    'name': ['First tick time', 'Last tick time', 'Closed positions', 'Orders total'],
                    'value': [first_tick_time_1, last_tick_time_1, closed_positions_1, orders_total_1],
                }

        first_instrument = pd.DataFrame(defaultInstrument_dict)
        first_instrument.set_index('name', inplace=True)

        return first_instrument

    def second_for_nine(self):

        secondInstrument = 0

        secondInstrument_dict = {
            'name': ['First tick time', 'Last tick time', 'Closed positions', 'Orders total'],
            'value': [0, 0, 0, 0],
        }

        soup = BeautifulSoup(self.html_text, "lxml")
        soup_str = str(soup.text).split('\n')

        for tr in soup.find_all('tr'):
            if '_aux_ins_CUX' in tr.text or '_aux_ins_CXU' in tr.text:
                secondInstrument = str('Instrument ' + tr.text[12:])

        for i in soup_str:
            if secondInstrument in i and secondInstrument != 0:
                first_tick_time_2 = (soup_str[soup_str.index(i) + 1][15:])
                last_tick_time_2 = (soup_str[soup_str.index(i) + 4][14:])
                closed_positions_2 = (soup_str[soup_str.index(i) + 8][16:])
                orders_total_2 = (soup_str[soup_str.index(i) + 9][12:])
                secondInstrument_dict = {
                    'name': ['First tick time', 'Last tick time', 'Closed positions', 'Orders total'],
                    'value': [first_tick_time_2, last_tick_time_2, closed_positions_2, orders_total_2],
                }

        second_instrument = pd.DataFrame(secondInstrument_dict)
        second_instrument.set_index('name', inplace=True)

        return second_instrument

    def tick_info_idx(self):

        if len(self.df) == 6:
            self.first_for_six()
            self.second_for_six()

        elif len(self.df) == 9:
            self.first_for_nine()
            self.second_for_nine()

    def event_log(self):
        event_log = 0
        if len(self.df) == 9:
            event_log_columns = ['Time', 'Event text']
            event_log_rows = self.df[8]['Event type'] == 'Commissions'
            event_log = self.df[8].loc[event_log_rows][event_log_columns]
            event_log['Event text'] = event_log['Event text'].str.replace('C', '', regex=True).str.replace('o', '', regex=True) \
                                                        .str.replace('m', '', regex=True).str.replace('i', '', regex=True) \
                                                        .str.replace('s', '', regex=True).str.replace('n', '', regex=True) \
                                                        .str.replace(' ', '', regex=True).str.replace('[', '', regex=True) \
                                                        .str.replace(']', '', regex=True).astype(float)
        elif len(self.df) == 6:
            event_log_columns = ['Time', 'Event text']
            event_log_rows = self.df[5]['Event type'] == 'Commissions'
            event_log = self.df[5].loc[event_log_rows][event_log_columns]
            event_log['Event text'] = event_log['Event text'].str.replace('C', '', regex=True).str.replace('o', '',
                                                                                                       regex=True) \
                .str.replace('m', '', regex=True).str.replace('i', '', regex=True) \
                .str.replace('s', '', regex=True).str.replace('n', '', regex=True) \
                .str.replace(' ', '', regex=True).str.replace('[', '', regex=True) \
                .str.replace(']', '', regex=True).astype(float)

        return event_log

    def closed_orders(self):
        closed_orders = self.df[4][
            ['Label', 'Direction', 'Open price', 'Close price', 'Profit/Loss', 'Profit/Loss in pips', 'Open date', 'Close date']]
        closed_orders.set_index('Label', inplace=True)
        return closed_orders

    def html_to_json(self):
        final_file = pd.DataFrame((self.header(), self.account_info(), self.parameters(), self.tick_info_idx(), self.event_log(), self.closed_orders()))
        return final_file.to_json('C:/Users/User/PycharmProjects/Roma/2010-2015/jsons/audnzd.json')


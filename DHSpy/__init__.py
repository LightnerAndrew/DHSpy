
'''
DHSpy - API Wrapper for USAID DHS Data
======================================

'''
# the basics 
import pandas as pd
from pandas import ExcelWriter

# packages for accessing the api
import json
from urllib.request import urlopen
import json
import requests

# access package location if needed. 
import pkg_resources


class query(object): 
    '''
    :attr url: the base url for the API. Default: https://api.dhsprogram.com/rest/dhs/. 
    :type url: str. 
    :attr series_codes: the series codes to download via the API. To search for series codes, use the `find_series_codes()` method. 
    :type series_codes: list 
    :attr country_codes: two-letter country codes of interest. To search for series codes, use the `find_country_codes()` method. 
    :type country_codes: list 
    :attr survey_codes: list of survey codes to download. To search for survey codes, use the `find_survey_codes()` method. 
    :type survey_codes: list     
    '''

    # parameters 
    url = 'https://api.dhsprogram.com/rest/dhs/'

    # select indicators 
    series_selection = []
    country_selection = []
    survey_selection = []


    ##### get the metadata for the queries. 

    def get_DHS_metadata(metadata_type, columns_interest=['IndicatorId', 'Label', 'Definition']):
        '''
        This function creates a pandas dataframe of the metadata selected in `metadata_type`. 
        
        :param metadata_type: the metadata of interest, known options = {'indicators', 'countries', 'surveys'}. 
        :type metadata_type: str
        :param columns_interest: columns to return in the dataframe, pass 'all' for all columns available. Default:  ['IndicatorId', 'Label', 'Definition']. 
        :type columns_interest: list
        
        return 
            pandas dataframe of metadata 
            
        '''
        # link to indicators
        url = 'https://api.dhsprogram.com/rest/dhs/'+metadata_type

        # request data from url
        req = urlopen(url)

        # read the json file
        resp = json.loads(req.read())

        # extract the data from the json
        json_data = resp['Data']

        # empty datafrmae to append data to
        final_data = pd.DataFrame.from_records(json_data)

        # select row of interest
        if columns_interest != 'all':
            final_data = final_data.loc[:, columns_interest]

        return final_data

    # use the function above to access  metadata of interest. 
    series_options = get_DHS_metadata('indicators')
    country_options = get_DHS_metadata('countries', columns_interest = ['CountryName', 'ISO2_CountryCode'])
    survey_options = get_DHS_metadata('surveys', ['SurveyId', 'SurveyYearLabel', 'SurveyType', 'CountryName'])


    ######################
    ### methods to access parameters 
    #######################

    def find_country_codes(self, country_names:list): 
        '''
        The find country codes of interest given a country name or list of country names 

        :param country_names: list of country names of interest
        :type country_names: list

        return 
            pandas.DataFrame()
        '''
        countries = self.country_options

        return countries.loc[countries['CountryName'].isin(country_names), :]


    ### eventually build the others. 

    def run(self): 
        '''
        Run the query given the series and survey selection. 
        '''

        return_data = pd.DataFrame()
        fails = []
        for survey in self.survey_selection: 

            for series in self.series_selection: 

                qry = '{}/indicators?={}/survey?={}'.format(self.url, series, survey)

                # try to access the data 
                try: 
                    # use urlopen to get initial response
                    req = urlopen(qry)

                    # read the json file (json is a type of format passed over internet which resembles python dictionarie)
                    resp = json.loads(req.read())

                    # select the data from the json
                    data_json = resp['Data']

                    # select the number of pages, this will be used to iterate over the pages to access the full dataset.
                    number_of_pages = resp['TotalPages']
                    print(number_of_pages)

                    # transform data_json into a pandas dataframe
                    data = pd.DataFrame.from_records(data_json)

                    # append data to final data 
                    return_data = return_data.append(data)

                except: 
                    fails.append((survey, series))

        return return_data



if __name__ =='__init__': 
    DHSpy = query()
    
        

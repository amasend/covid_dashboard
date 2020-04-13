from typing import TYPE_CHECKING, List
import json

from postman_covid19_sdk.client import APIClient
from postman_covid19_sdk.utils.enums import StatusType
from pandas import DataFrame

if TYPE_CHECKING:
    from pandas import Series


class DataManager:
    def __init__(self):
        self.client = APIClient()
        self.locations = self.load_locations()

        # note: data for the first location
        self.data_confirmed = None
        self.data_recovered = None
        self.data_deaths = None
        self.prev_location = 'POLAND'
        # --- end note

        # note: data for the second location to compare with
        self.data_confirmed2 = None
        self.data_recovered2 = None
        self.data_deaths2 = None
        self.prev_location2 = None
        # --- end note

    @staticmethod
    def load_locations(path: str = "../location_list.json") -> dict:
        """
        Load locations data into the memory.

        Parameters
        ----------
        path: str, optional
            Local path to the data file.

        Returns
        -------
        Dictionary with locations.
        """
        with open(path, 'r') as f:
            locations = json.loads(f.read())
        return locations

    @staticmethod
    def remove_duplicated(data: 'DataFrame') -> 'DataFrame':
        """
        Sometimes for some countries there are duplicated entries in one day.
        This should remove a duplicate entry and return a row with a max case number.

        Parameters
        ----------
        data: DataFrame, required
            Pandas DataFrame with data to clean.

        Returns
        -------
        Pandas DataFrame with cleaned data
        """
        data = DataFrame(data=data['Cases']).resample('D').sum()
        return data.iloc[:-1]

        # data = data.loc[(data['Province'] == '') & (data['City'] == '')]
        # idx = data.groupby(level=0)['Cases'].transform(max) == data['Cases']
        # return data[idx]

    @staticmethod
    def clean_data(data: 'Series') -> List[float]:
        """
        Clean Cases data, there should be growing or constant number of cases
        along the timeline per country per API specification. Sometimes there are incorrect numbers,
        this tries to get rid of incorrect data and replace them with the next correct case.
        It could introduce some mismatch but this mismatch is already introduced by the API.

        Parameters
        ----------
        data: Series, required
            Pandas Series with number of Cases (need to be in chronological order)

        Returns
        -------
        List of float numbers (corrected data)
        """

        data = [case for case in data]
        data = data[::-1]

        for i, val in enumerate(data):
            if i > 0:
                if val > data[i - 1]:
                    data[i] = data[i - 1]

        return data[::-1]

    def download_data_for_location_one(self, location) -> None:
        """
        Download data for the first location from COVID19 API.

        Parameters
        ----------
        location: str/None, required
            Location name, if None data for the default location will be downloaded (POLAND)
        """
        if location:
            self.data_confirmed = self.remove_duplicated(self.client.get_by_country(
                country=self.client.Countries.__dict__[location]))
            self.data_recovered = self.remove_duplicated(self.client.get_by_country(
                country=self.client.Countries.__dict__[location],
                status=StatusType.RECOVERED))
            self.data_deaths = self.remove_duplicated(self.client.get_by_country(
                country=self.client.Countries.__dict__[location],
                status=StatusType.DEATHS))

        else:
            self.data_confirmed = self.remove_duplicated(self.client.get_by_country(
                country=self.client.Countries.POLAND))
            self.data_recovered = self.remove_duplicated(self.client.get_by_country(
                country=self.client.Countries.POLAND, status=StatusType.RECOVERED))
            self.data_deaths = self.remove_duplicated(self.client.get_by_country(
                country=self.client.Countries.POLAND, status=StatusType.DEATHS))

        self.data_confirmed['Cases'] = self.clean_data(data=self.data_confirmed['Cases'])
        self.data_recovered['Cases'] = self.clean_data(data=self.data_recovered['Cases'])
        self.data_deaths['Cases'] = self.clean_data(data=self.data_deaths['Cases'])

        self.data_confirmed.index = self.data_confirmed.index.tz_localize(None)
        self.data_recovered.index = self.data_recovered.index.tz_localize(None)
        self.data_deaths.index = self.data_deaths.index.tz_localize(None)

    def download_data_for_location_two(self, location) -> None:
        """
        Download data for the second location from COVID19 API.

        Parameters
        ----------
        location: str, required
            Location name.
        """
        if location:
            self.data_confirmed2 = self.remove_duplicated(self.client.get_by_country(
                country=self.client.Countries.__dict__[location]))
            self.data_recovered2 = self.remove_duplicated(self.client.get_by_country(
                country=self.client.Countries.__dict__[location],
                status=StatusType.RECOVERED))
            self.data_deaths2 = self.remove_duplicated(self.client.get_by_country(
                country=self.client.Countries.__dict__[location],
                status=StatusType.DEATHS))

            self.data_confirmed2['Cases'] = self.clean_data(data=self.data_confirmed2['Cases'])
            self.data_recovered2['Cases'] = self.clean_data(data=self.data_recovered2['Cases'])
            self.data_deaths2['Cases'] = self.clean_data(data=self.data_deaths2['Cases'])

            self.data_confirmed2.index = self.data_confirmed2.index.tz_localize(None)
            self.data_recovered2.index = self.data_recovered2.index.tz_localize(None)
            self.data_deaths2.index = self.data_deaths2.index.tz_localize(None)
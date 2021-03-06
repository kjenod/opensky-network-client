"""
Copyright 2019 EUROCONTROL
==========================================

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following
   disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
   disclaimer in the documentation and/or other materials provided with the distribution.
3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products
   derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

==========================================

Editorial note: this license is an instance of the BSD license template as provided by the Open Source Initiative:
http://opensource.org/licenses/BSD-3-Clause

Details on EUROCONTROL: http://www.eurocontrol.int
"""

import typing as t
from datetime import datetime

from rest_client import Requestor, ClientFactory
from rest_client.typing import RequestHandler
from opensky_network_client.models import States, BoundingBox, FlightConnection, Airport

__author__ = "EUROCONTROL (SWIM)"

Timestamp = t.TypeVar('Timestamp', int, datetime)
ICAO24 = t.Union[str, t.List[str]]


class OpenskyNetworkClient(Requestor, ClientFactory):
    def __init__(self, request_handler: RequestHandler) -> None:
        """
        :param request_handler: an instance of an object capable of handling http requests, i.e. requests.session()
        """
        Requestor.__init__(self, request_handler)
        self._request_handler = request_handler

        self._url_states = 'api/states/all/'
        self._url_flights_arrival = 'api/flights/arrival/'
        self._url_flights_departure = 'api/flights/departure/'
        self._url_airport = 'api/airports/'

    def get_states(self,
                   timestamp: Timestamp = 0,
                   icao24: t.Optional[ICAO24] = None,
                   bbox: t.Optional[BoundingBox] = None,
                   json: t.Optional[bool] = False) -> States:
        """
        :param timestamp: the time in seconds since Unix epoch or datetime. Current time will be used if omitted.
        :param icao24: one or more ICAO24 transponder addresses represented by a hex string (e.g. abc9f3). If omitted,
                       the state vectors of all aircraft are returned.
        :param bbox: a bounding box of WGS84 coordinates to query a certain area
        """
        if isinstance(timestamp, datetime):
            timestamp = int(timestamp.timestamp())

        kwargs = {
            'extra_params': {
                "time": timestamp,
            }
        }

        if icao24 is not None:
            kwargs['extra_params'].update({"icao24": icao24})

        if bbox is not None:
            kwargs['extra_params'].update(bbox.to_json())

        if not json:
            kwargs.update({'response_class': States})

        response = self.perform_request('GET', self._url_states, **kwargs)

        return response

    def get_flight_arrivals(self,
                            airport: str,
                            begin: Timestamp,
                            end: Timestamp,
                            json: t.Optional[bool] = False) -> t.List[FlightConnection]:
        """
        :param airport: ICAO identier for the airport
        :param begin: Start of time interval to retrieve flights for as Unix time (seconds since epoch) or datetime
        :param end: End of time interval to retrieve flights for as Unix time (seconds since epoch) or datetime
        """
        kwargs = {
            'extra_params': self._prepare_flight_connection_parameters(airport, begin, end),
            'many': True
        }

        if not json:
            kwargs.update({'response_class': FlightConnection})

        response = self.perform_request('GET', self._url_flights_arrival, **kwargs)

        return response

    def get_flight_departures(self,
                              airport: str,
                              begin: Timestamp,
                              end: Timestamp,
                              json: t.Optional[bool] = False) -> t.List[FlightConnection]:
        """
        :param airport: ICAO identier for the airport
        :param begin: Start of time interval to retrieve flights for as Unix time (seconds since epoch) or datetime
        :param end: End of time interval to retrieve flights for as Unix time (seconds since epoch) or datetime
        """
        kwargs = {
            'extra_params': self._prepare_flight_connection_parameters(airport, begin, end),
            'many': True
        }

        if not json:
            kwargs.update({'response_class': FlightConnection})

        response = self.perform_request('GET', self._url_flights_departure, **kwargs)

        return response

    def get_airport(self, icao: str, json: t.Optional[bool] = False) -> Airport:
        """
        :param icao: ICAO identier for the airport
        """
        kwargs = {
            'extra_params': {
                "icao": icao,
            }
        }

        if not json:
            kwargs.update({'response_class': Airport})

        response = self.perform_request('GET', self._url_airport, **kwargs)

        return response

    @staticmethod
    def _prepare_flight_connection_parameters(airport: str,
                                              begin: Timestamp,
                                              end: Timestamp) -> t.Dict[str, t.Union[str, int]]:
        if isinstance(begin, datetime):
            begin = int(begin.timestamp())

        if isinstance(end, datetime):
            end = int(end.timestamp())

        return {
            "airport": airport,
            "begin": begin,
            "end": end
        }

import logging
import requests

from private.dispatch_settings import *
from private.secret_settings import *

logger = logging.getLogger('geocoder')


def compile_incident_location_string(incident_dict):
    """
    Gather the required search text from the incident dict.
    """
    loc_string = ''
    for key in STREET_ADDRESS_KEYS:
        if key in incident_dict:
            loc_string += str(incident_dict[key]) + ', '
        else:
            logger.warn("No value for key %s" % key)

    for key in VENUE_KEYS:
        if key in incident_dict:
            loc_string += str(incident_dict[key])
        else:
            logger.warn("No value for key %s" % key)

    incident_location_string = (loc_string.lower().title()).encode('utf-8')

    return incident_location_string


def geocode(incident_location_string, from_sensor=False, strict=True, round=1):
    """
    Uses the unauthenticated Google Maps API V3.  using passed incident location string, return a latitude and logitude for an incident.
    """

    logger.info("Geocoding %s ..." % incident_location_string)

    if incident_location_string == '' or incident_location_string is None:
        logger.error('Empty incident strings cannot be geocoded.')
        raise ValueError('Empty incident strings cannot be geocoded.')


    url = 'https://maps.googleapis.com/maps/api/geocode/json?'

    geocoder_restrictions = "country:" + LOCALE_COUNTRY + "|administrative_area:" + LOCALE_STATE

    if strict is True:
        geocoder_restrictions += "|administrative_area:" + LOCALE_ADMIN_REGION

    params = {
        'key': GOOGLE_SERVER_KEY,
        'address': incident_location_string,
        'sensor': "true" if from_sensor else "false",
        'components': geocoder_restrictions
        }

    re = requests.get(url=url, params=params)

    if re.status_code == 200:
        response = re.json()

        if "error_message" in response:
            latitude, longitude = None, None
            error = response["status"]
            reason = response["error_message"]
            payload = incident_location_string
            logger.error("Failed to generate coordinates for an Incident\n Status: %s\n Reason: %s\n Payload: %s" % \
                         (error, reason, payload))

        elif response['status'] == "ZERO_RESULTS":
            if round == 1:
                geocode(incident_location_string, strict=False, round=2)
                logger.info("Zero results for %s \n trying again with strict = False" % incident_location_string)
            elif round == 2:
                # Do something more recursive, again...?
                logger.warn("No Location Found after removing strict filtration. Payload: %s" % incident_location_string)
                latitude, longitude = None, None

        elif response['status'] == 'OK':
            result = response['results'][0]['geometry']
            location = result['location']
            accuracy = result['location_type']
            latitude, longitude = location['lat'], location['lng']

            logger.info(incident_location_string, accuracy, latitude, longitude)

        else:
            latitude, longitude = None, None
            reason = response["status"]
            logger.warn(incident_location_string, "Could not generate coordinates for this Incident - Reason: %s" % reason)
    else:
        logger.error("%s" % re.status_code)
        # Do Something!

    return latitude, longitude

from datetime import datetime
import requests
import json
from waste_collection_schedule import Collection
from waste_collection_schedule.exceptions import SourceArgumentNotFound, SourceArgumentNotFoundWithSuggestions
import logging

_LOGGER = logging.getLogger(__name__)

TITLE = "Aalborg Kommune - Mit Affald"
DESCRIPTION = "Source for Aalborg Municipality, Denmark through Mit Affald on renoweb.dk"
URL = "https://aalborg.renoweb.dk/Legacy/selvbetjening/mit_affald.aspx"
TEST_CASES = {
    "simple-stree-no": {"address": "Naboløs 2"},
    "simple-street-no-city": {"address": "Riishøjsvej 91, 9000 Aalborg"},
    "full-with-nrs": {"address": "Havnegade 2, 9370 Hals (Ejd.nr. 617840, BFE.nr. 7223374)"},
}

API_URL = "https://aalborg.renoweb.dk/Legacy/JService.asmx"
ICON_MAP = {   # Optional: Dict of waste types and suitable mdi icons
    "Restaffald": "mdi:trash-can",
    "Genbrug": "mdi:recycle",
    "Haveaffald": "mdi:leaf",
    "Farligt": "mdi:danger",
}

#### Arguments affecting the configuration GUI ####

HOW_TO_GET_ARGUMENTS_DESCRIPTION = {
    "en": f"Enter address which matches yours on {URL}, okay to include the '(Ejd.nr. XX, BFE.nr. YY)'",
}

PARAM_DESCRIPTIONS = {
    "en": {
        "address": "Address",
    },
}

#### End of arguments affecting the configuration GUI ####

class Source:
    def __init__(self, address:str):
        self._address = address
        self.__adrid = None

    @property
    def _adrid(self):
        if self.__adrid is None:
            req = requests.post(
                f"{API_URL}/Adresse_SearchByString",
                json={
                    # Remove potential "(Ejd.nr. 617840, BFE.nr. 7223374)" part from address search string
                    "searchterm": self._address.split("(")[0].strip(),
                    "addresswithmateriel": 0,
                }
            )
            results = self._unpacklist(req.json())

            if len(results) > 1:
                # Address matching is some kind of fuzzy search
                # Let's see if the entered address matches only one result.
                # Possible since search does not support parenthesis part as searchterm
                if len((results := [res for res in results if self._address in res["label"]])) == 1:
                    _LOGGER.info("Found unique address '%s'", results[0]["label"])
                else:
                    raise SourceArgumentNotFoundWithSuggestions(
                        "address",
                        self._address,
                        (addr['label'].strip() for addr in results)
                    )
            res = results[0]

            if res["value"] == "0000":
                raise SourceArgumentNotFound("address", self._address, f"No results. API Error: {res['label']}")

            self.__adrid = res["value"]
        return self.__adrid

    @staticmethod
    def _unpacklist(json_data: dict) -> list[dict]:
        return json.loads(json_data["d"])["list"]

    def _fetch_plan(self):
        # Use dict to remote duplicates
        collections = {}
        req = requests.post(f"{API_URL}/GetAffaldsplanMateriel_mitAffald", json={"adrid": self._adrid, "common":False})
        for waste_entry in self._unpacklist(req.json()):
            if " den " not in waste_entry["toemningsdato"]:
                continue
            waste_type = waste_entry["ordningnavn"].split(" ")[0]
            cal_req = requests.post(f"{API_URL}/GetCalender_mitAffald", json={"materialid": waste_entry["id"]})
            for waste_date in self._unpacklist(cal_req.json()):
                date_str = waste_date.split(" ")[-1]
                collections[(date_str, waste_type)] = Collection(
                    date=datetime.strptime(date_str, "%d-%m-%Y").date(),
                    t=waste_type,
                    icon=ICON_MAP.get(waste_type),
                )
        return collections.values()



    def fetch(self) -> list[Collection]:
        return list(self._fetch_plan())  # List that holds collection schedule


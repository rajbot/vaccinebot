from collections import namedtuple

County = namedtuple("County", ["name", "url"])

counties = {
    "alameda": County(name="Alameda", url="https://covid-19.acgov.org/vaccines"),
    "butte": County(name="Butte", url="https://www.buttecounty.net/ph/COVID19/vaccine"),
    "calaveras": County(
        name="Calaveras", url="https://covid19.calaverasgov.us/Vaccines"
    ),
    "colusa": County(name="Colusa", url="https://www.countyofcolusa.org/771/COVID19"),
    "contracosta": County(
        name="Contra Costa", url="https://www.coronavirus.cchealth.org/vaccine"
    ),
    "delnorte": County(name="Del Norte", url="https://www.covid19.dnco.org/vaccines"),
    "sanfrancisco": County(
        name="San Francisco", url="https://sf.gov/get-vaccinated-against-covid-19"
    ),
}

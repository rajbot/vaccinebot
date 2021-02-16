from collections import namedtuple

County = namedtuple("County", ["name", "url"])

counties = {
    "alameda": County(name="Alameda", url="https://covid-19.acgov.org/vaccines"),
    "sanfrancisco": County(
        name="San Francisco", url="https://sf.gov/get-vaccinated-against-covid-19"
    ),
}

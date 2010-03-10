"""
	taken from http://developer.yahoo.com/geo/geoplanet/guide/concepts.html#woeidsplanet

Continent
	One of the major land masses on the earth. GeoPlanet is built on a seven continent model: Asia (24865671), Africa (24865670), North America (24865672), South America (24865673), Antarctica (28289421), Europe (24865675), and Pacific (Australia, New Zealand, and the other islands in the Pacific Ocean -- 24865674).
Country
	One of the countries and dependent territories defined by the ISO 3166-1 standard.
Admin1
	One of the primary administrative areas within a country. Place type names associated with this place type include: State, Province, Prefecture, Country, Region, Federal District.
Admin2
	One of the secondary administrative areas within a country. Place type names associated with this place type include: County, Province, Parish, Department, District.
Admin3
	One of the tertiary administrative areas within a country. Place type names associated with this place type include: Commune, Municipality, District, Ward.
Town
	One of the major populated places within a country. This category includes incorporated cities and towns, major unincorporated towns and villages.
Suburb
	One of the subdivisions within a town. This category includes suburbs, neighborhoods, wards.
Postal Code
	One of the postal code areas within a country. This category includes both full postal codes (such as those in UK and CA) and partial postal codes. Examples include: SW1A 0AA (UK), 90210 (US), 179-0074 (JP).
Supername
	A place that refers to a region consisting of multiple countries or an historical country that has been dissolved into current countries. Examples include Scandinavia, Latin America, USSR, Yugoslavia, Western Europe, and Central America.
Colloquial
	Examples are New England, French Riviera, Kansai Region, South East England, Pacific States, and Chubu Region.
Time Zone
	A place that refers to an area defined by the Olson standard. Examples include America/Los Angeles, Asia/Tokyo, Europe/Madrid.
"""

PLACE_TYPES = {
	'Continent': 110,
	'Time Zone': 100,
	'Supername': 90,
	'Country': 80,
	'Admin1': 70,
	'Admin2': 60,
	'Colloquial': 50,
	# LOCAL BELOW HERE...
	'Admin3': 40,
	'Town': 30,
	'Suburb': 20,
	'Postal Code': 10,
	'Zip': 10,
	}

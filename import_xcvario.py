from urllib import request
import re
import glider.polar as gp

XCVARIO_POLARS_DATA_URL = 'https://raw.githubusercontent.com/iltis42/XCVario/master/main/Polars.cpp'

# Load polars from json file
polars_db = gp.PolarsDB.get_instance('./glider-polars-db.json')

# Load XCVario Polar Store
data = request.urlopen(XCVARIO_POLARS_DATA_URL).read().decode('utf-8')
print('Size of the glide polars db is {}'.format(len(polars_db.polars_db)))

regex = r"{\s*[0-9,]*\s*\"(?P<glider>.*)\"[^,]*,\s*(?P<wing_load>[0-9-.]*),\s*(?P<speed1>[0-9-.]*),\s*(?P<sink1>[0-9-.]*),\s*(?P<speed2>[0-9-.]*),\s*(?P<sink2>[0-9-.]*),\s*(?P<speed3>[0-9-.]*),\s*(?P<sink3>[0-9-.]*),\s*(?P<max_ballast>[0-9-.]*),\s*(?P<wing_area>[0-9-.]*)\s*}"

# Add XCVArio polars to the DB
matches = re.finditer(regex, data, re.MULTILINE)
for match in matches:
	new_polar = dict()
	try:
		new_polar['name'] = match.group('glider').replace('/','-')
		new_polar['max ballast'] = float(match.group('max_ballast'))
		new_polar['wing_area'] = float(match.group('wing_area'))
		new_polar['method'] = '3-points'
		new_polar['source'] = 'XCVario'
		new_polar['wing_loading'] = float(match.group('wing_load'))
		new_polar['speed'] = [float(match.group('speed1')), float(match.group('speed2')), float(match.group('speed3'))]
		new_polar['sink_rate'] = [float(match.group('sink1')), float(match.group('sink2')), float(match.group('sink3'))]

		# polars_db.polars_db.append(new_polar)
		if new_polar['name'] != 'User Polar':
			polars_db.add(new_polar)
			print('Adding {}'.format(new_polar['name']))
	except ZeroDivisionError as ze:
		print('Error for {}, wing area is {} => {}'.format(new_polar['name'], match.group('wing_area'),ze))
	except Exception as e:
		print('Error for {} => {}'.format(new_polar['name'], e))
	
print('Size of the glide polars db is {}'.format(len(polars_db.polars_db)))

# Save the polars db to json
polars_db.save('./glider-polars-db.json')
print('New Polars DB save to file xx')

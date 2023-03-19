import numpy as np
from scipy.optimize import fsolve
import json
import math
import pandas as pd
from abc import ABC, abstractmethod

KM_TO_MS = 3.6				# factor to convert km/h in m/s
CONVERT_TO_MS = False		# True if we want to convert speed from km/h to m/s

POLAR_CURVE_START_KM = 50		# in km/h
POLAR_CURVE_END_KM = 230		# in km/h

POLAR_CURVE_START = (POLAR_CURVE_START_KM / KM_TO_MS) if CONVERT_TO_MS else POLAR_CURVE_START_KM
POLAR_CURVE_END = (POLAR_CURVE_END_KM / KM_TO_MS) if CONVERT_TO_MS else POLAR_CURVE_END_KM

# POLAR_CURVE_NBR_SAMPLE = 33
POLAR_CURVE_NBR_SAMPLE =  int(((POLAR_CURVE_END - POLAR_CURVE_START) // 5) +1)

# to convert speed from km/h to m/s
xaxis_unit = lambda x: x / (KM_TO_MS if CONVERT_TO_MS else 1)

class PolarGlider(ABC):
	def __init__(self, name, source, wing_area, max_ballast, wing_loading = None, weight = None):
		if (wing_area <= 0): 
			raise ValueError('Invalide wing area, value (must be  > 0)')

		if (weight is None) and (wing_loading is None):
			raise ValueError('You need to specify either wing_loading or weight for glider {}-{}'.format(name, source))

		if (weight is not None) and (wing_loading is not None):
			if (weight / wing_area != wing_loading):
				raise ValueError('{} - {}, Wing loading is {}kg/m2 instead of {:0.2f}kg/m2 for a weight of {}kg and a wing area of {}m2'.format(name, source, wing_loading, (weight / wing_area), weight, wing_area))

		if (wing_loading is None):
			wing_loading = round(weight / wing_area,2)

		if (weight is None):
			weight = wing_loading * wing_area

		self.name = name
		self.source = source
		self.wing_area = wing_area
		self.max_ballast = max_ballast
		self.weight = weight

		self.polynomial = np.polymul(np.poly1d([1.2,-1.6, 0.8 ]),-1)		# init to a default polynomial
		self.init_polynomial = self.polynomial

		self.wing_loading = wing_loading
		self.init_wing_loading = self.wing_loading

	def update_wing_loading(self, new_wing_loading):
		# if self.spec['method'] == 'ABC':
		# 	x = [self.spec["A"],self.spec["B"], self.spec["C"]]
		# 	y = self.polynomial(x)
		# elif self.spec['method'] == '3-points':
		# 	x = [xaxis_unit(s) for s in self.spec['speed']]
		# 	y = self.spec['sink_rate']
		# else:
		# 	raise Exception('Unknow glider polar method: {}'.format(self.spec['method']))

		x = np.linspace(POLAR_CURVE_START,POLAR_CURVE_END,POLAR_CURVE_NBR_SAMPLE)
		y = self.curve(x)

		new_x = [ vi * math.sqrt(new_wing_loading/self.wing_loading) for vi in x]
		new_y = [ vz * math.sqrt(new_wing_loading/self.wing_loading) for vz in y]
		
		# update the polynomial
		self.wing_loading = new_wing_loading
		self.polynomial = np.poly1d(np.polyfit(new_x, new_y, 2))
		
	def curve(self,x):
		return self.polynomial(x)

	@abstractmethod
	def method(self):
		pass

	def init_curve(self,x):
		return self.init_polynomial(x)

	def get_min_sink_rate(self):
		a = self.polynomial.coefficients[0]
		b = self.polynomial.coefficients[1]
		c = self.polynomial.coefficients[2]

		msr_speed = -b/(2*a) 
		msr_vz = a * np.power(msr_speed,2) +b* msr_speed + c
		msr_ld = -msr_speed/(KM_TO_MS*msr_vz)

		return msr_speed, msr_vz, msr_ld

	def get_max_glide_ratio(self):
		a = self.polynomial.coefficients[0]
		b = self.polynomial.coefficients[1]
		c = self.polynomial.coefficients[2]

		k = b - np.sqrt(4 * a * c)
		mgr_speed = -(b - k) / (2 * a)
		mgr_vz = a * np.power(mgr_speed,2) + b * mgr_speed + c
		mgr_ld = -mgr_speed/(KM_TO_MS*mgr_vz)

		return mgr_speed, mgr_vz, mgr_ld
	
	def __tangent_horizontal(self, f,fprime,x):
		roots = fsolve(lambda x: fprime(x), x)
		y = f(roots)
		m = fprime(roots)
		return y - m * (x - roots)

	def __tangent_at_origin(self, f, fprime, x):
		roots_estimate = 100,
		roots =fsolve(lambda u: f(u) - fprime(u)*u, roots_estimate)
		return fprime(roots)*x 

	def __intersection(self, x, tangent, f, df):
		roots = fsolve(lambda x: tangent(f,df,x) - f(x), x)
		return roots, f(roots)

	def tangent_horizontal(self, tg_x):
		a = self.polynomial.coefficients[0]
		b = self.polynomial.coefficients[1]
		c = self.polynomial.coefficients[2]
		
		f = lambda x: a*np.power(x,2) + b*x + c
		df = lambda x: 2*a*x + b

		tgh_y = self.__tangent_horizontal(f, df, tg_x)
		x_int, y_int = self.__intersection(100,self.__tangent_horizontal,f,df)

		return tgh_y, x_int, y_int

	def tangent_at_origin(self, tg_x):
		a = self.polynomial.coefficients[0]
		b = self.polynomial.coefficients[1]
		c = self.polynomial.coefficients[2]
		
		f = lambda x: a*np.power(x,2) + b*x + c
		df = lambda x: 2*a*x + b

		tgao_y = self.__tangent_at_origin(f, df, tg_x)
		x_int, y_int = self.__intersection(100,self.__tangent_at_origin,f,df)

		return tgao_y, x_int, y_int

	@staticmethod
	def factory(config):
		if (config['method'] =='ABC'):
			return PolarGliderABC(
				config['name'],
				config['source'],
				config['wing_area'],
				config['max ballast'],
				config['A'],
				config['B'],
				config['C'],
				config['wing_loading'] if 'wing_loading' in config else None,
				config['weight'] if 'weight' in config else None
			)
		elif (config['method'] =='3-points'):
			return PolarGlider3Points(
				config['name'],
				config['source'],
				config['wing_area'],
				config['max ballast'],
				config['speed'],
				config['sink_rate'],
				config['wing_loading'] if 'wing_loading' in config else None,
				config['weight'] if 'weight' in config else None 
			)
		else:
			raise Exception("Unkknow method {}.".format(config['method']))

class PolarGlider3Points(PolarGlider):
	def __init__(self, name, source, wing_area, max_ballast, speed, sink_rate,  wing_loading = None, weight = None ):
		PolarGlider.__init__(self, name, source, wing_area, max_ballast, wing_loading , weight )
		self.speed = speed
		self.sink_rate = sink_rate

		speeds_converted = [xaxis_unit(x) for x in speed]
		self.polynomial = np.poly1d(np.polyfit(speeds_converted, sink_rate, 2))
		self.init_polynomial = self.polynomial

	def method(self):
		return '3-points'

class PolarGliderABC(PolarGlider):
	def __init__(self, name, source, wing_area, max_ballast, a, b, c, wing_loading = None, weight = None ):
		PolarGlider.__init__(self, name, source, wing_area, max_ballast, wing_loading , weight )
		self.A = a
		self.B = b
		self.C = c

		self.polynomial = np.polymul(np.poly1d([a,b, c ]),-1)
		self.init_polynomial = self.polynomial

	def curve(self,x):
		return self.polynomial(np.divide(x,100))
	
	def init_curve(self,x):
		return self.init_polynomial(np.divide(x,100))
	
	def tangent_at_origin(self, tg_x):
		tgao_y, x_int, y_int = super().tangent_at_origin(np.divide(tg_x,100))
		return tgao_y, x_int*100, y_int

	def tangent_horizontal(self, tg_x):
		tgh_y, x_int, y_int = super().tangent_horizontal(np.divide(tg_x,100))
		return tgh_y, x_int*100, y_int

	def get_min_sink_rate(self):
		a = self.polynomial.coefficients[0]
		b = self.polynomial.coefficients[1]
		c = self.polynomial.coefficients[2]

		msr_speed = -b/(2*a) * 100
		msr_vz = a * np.power(msr_speed/100,2) +b*msr_speed/100 + c
		msr_ld = -msr_speed/(KM_TO_MS*msr_vz)

		return msr_speed, msr_vz, msr_ld

	def get_max_glide_ratio(self):
		a = self.polynomial.coefficients[0]
		b = self.polynomial.coefficients[1]
		c = self.polynomial.coefficients[2]

		k = b - np.sqrt(4 * a * c)
		mgr_speed = -(b - k) / (2 * a) * 100
		mgr_vz = a * np.power(mgr_speed/100,2) + b * mgr_speed/100 + c
		mgr_ld = -mgr_speed/(KM_TO_MS*mgr_vz)

		return mgr_speed, mgr_vz, mgr_ld

	def update_wing_loading(self, new_wing_loading):
		x = np.linspace(POLAR_CURVE_START,POLAR_CURVE_END,POLAR_CURVE_NBR_SAMPLE)
		y = self.curve(x)

		new_x = [ vi/100 * math.sqrt(new_wing_loading/self.wing_loading) for vi in x]
		new_y = [ vz * math.sqrt(new_wing_loading/self.wing_loading) for vz in y]

		# update the polynomial
		self.wing_loading = new_wing_loading
		self.polynomial = np.poly1d(np.polyfit(new_x, new_y, 2))

	def method(self):
		return 'ABC'

class PolarsDB:
	__instance = None

	def __init__(self, json_file):
		if PolarsDB.__instance is not None :
			raise Exception("get_instance() has to be call to return an object.")

		with open(json_file) as json_file:
			self.polars_db = json.load(json_file)

	def findByMethod(self, methods = ['3-points', 'ABC', 'by-hand']):
		res= []
		for x in self.polars_db:
			if  x['method'] in methods:
				res.append('{} / {}'.format(x['name'], x['source']))
		return res

	def fromNameAndSource(self, glider_name, source):
		filtered_db = []

		# Iterate over all the items in dictionary
		for elem in self.polars_db:
			# Check if item satisfy the given condition then add to new dict
			if elem['name'] == glider_name and elem['source'] == source:
				filtered_db.append(elem)

		if len(filtered_db) > 1:
			raise Exception('More than one entry with glider name {} and source {}'.format(glider_name, source) )
	
		if len(filtered_db) == 0:
			raise Exception('No entry with glider name {} and source {}'.format(glider_name, source) )

		return PolarGlider.factory(filtered_db[0])
		
	@staticmethod
	def get_instance(json_file = None):
		if PolarsDB.__instance is None :
			if (json_file is None):
				raise ValueError('json file name cannot be null')

			PolarsDB.__instance = PolarsDB(json_file)
		return PolarsDB.__instance

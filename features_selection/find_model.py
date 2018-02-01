import numpy as np
import scipy as sp
import copy
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import Ridge, LinearRegression
import pandas as pd
import mysql.connector
import os
import datetime as dt
from itertools import chain
import constants
import warnings
import csv
from tempfile import TemporaryFile  


class data():
	def __init__(self):
		self.name = data;
                self.feature_numbers = list()
		self.current_features = list()
		self.current_labels = list()
		self.best_r = 0;
	
	def read_in_data(self, f_name):
		f = []
		targets = []
		label = []
		with open(f_name, 'r') as csvfile:
			spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
			i = 0
			for row in spamreader:
				if i == 0:
					for item in row[0].split(','):
						
						label.append(item)
					item_length = len(row[0].split(','))
					i = i + 1
					continue
				line = []
				j = 0
				for item in row[0].split(','):
					 j = j + 1
					 if j == item_length:
						targets.append(float(item))
						continue
					 line.append(float(item))
				f.append(line)
		self.labels = list(label)
		self.targets = list(targets)
		self.features = list(f)
		self.l_features = len(label)
		self.zip_features = map(list, zip(*f))
					 
	def print_features(self):
		print self.features		

	def print_zip_features(self):
		print self.zip_features		


	def print_targets(self):
		print self.targets

	def print_labels(self):
		print self.labels

	def length_features(self):
		return self.l_features
	
	def get_current_feat(self):
		return self.feature_numbers
	
        def get_current_labels(self):
		return self.current_labels

	def set_features(self):
                self.current_features = list()
            
                for feat in self.feature_numbers:

                    if len(self.current_features) == 0:
                        for item in self.zip_features[feat]:
                            self.current_features.append([item])
                    else:
                        num = 0
                        for item in self.zip_features[feat]:
                            self.current_features[num].append(item)
                            num = num +1

        def add_feature_num(self, i):
                self.feature_numbers.append(i)

	def add_labels(self, i):
		self.current_labels.append(self.labels[i])

	def gen_perms(self,j):
                self.set_features()
                predictors = copy.copy(self.current_features[:])
  		labels = list(self.current_labels)
		labels.append(self.labels[j])
		if len(predictors) == 0:
			for item in self.zip_features[j]:
				predictors.append([item])	
 			return predictors, labels
  		
		
 		for i in range(len(predictors)): # loop through all unused features
			
    			predictors[i].append(self.features[i][j])
  
  
 		return predictors, labels
  

model = data();
model.read_in_data("good_futures.csv")
#model.print_features()
#model.print_zip_features()
targets = model.targets

values = model.length_features()

top_r = -1
current_adding = -1 
importance = []
#for i in range(1): 
for i in range(values -1): 
  for j in range(values -1):
    mods = model.get_current_feat() 
    if j not in mods: # if its already in our model skip it
    	predictors, labels = model.gen_perms(j) # model (actual values), 
    else:
      continue
  
 
    testX = np.asarray(predictors)
    testY = np.asarray(targets)
    # theta initialization
    theta = np.zeros(((len(predictors) + 1), 1))
    theta = np.transpose(theta)
    
    ridge = Ridge(alpha=4, fit_intercept=False, normalize=True)                                                                                                                                                                                                                 
    ridge.fit(testX, testY)
    r_value  = ridge.score(testX, testY) 

    adjusted_r_value = 1 - (((1 - (r_value))*(len(testY) -1))/(len(testY) - len(labels) - 1) )
    print adjusted_r_value, r_value
    importance.append((labels[0], r_value))
    sorted_importance = sorted(importance, key=lambda tup: tup[1])
    if adjusted_r_value > top_r:
	current_adding = j
	top_r = adjusted_r_value
	new_labels = labels


  
#  for i in range(len(sorted_importance)):
 #   cat, points = sorted_importance[len(sorted_importance) -1 -i ]
  #  print cat, points 

  model.add_feature_num(current_adding)
  model.set_features()
  model.add_labels(current_adding)
  print "Choice", model.get_current_labels(), top_r


  #print new_labels, top_r


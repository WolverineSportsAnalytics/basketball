''' This is a base class that will have direct methods for implimenting machine learning algorthms and being imported and used '''

class Algorithm():
    def __init__(self, data):
        self.data = data
        self.split_data()

    def split_data(self):
        ''' This will split data and allow you to do feature selection here'''
        raise NotImplementedError # must be overwritten by other class

    def predict(self):
        ''' This abstract method needs to be implimented in any child class '''
        ''' Predict method returns predicts for the input data '''
        raise NotImplementedError # must be overwritten by other class

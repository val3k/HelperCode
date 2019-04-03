# -*- coding: utf-8 -*-
"""
Created on Tue Apr  2 10:22:38 2019

@author: razrab
"""
import os
import face_recognition

os.chdir('C:\\Users\\razrab\\Desktop\\WFlow\\Tasks\\vision\\face_recognition_web')

class FaceComp:
    def __init__(self, folder):
        self.folder = folder
        self.images = []
        self.names = []
        self.faces = []
        
        self.get_images_names()
        self.get_encodings()
        pass
    
    
    def get_images_names(self):
        for (dirpath, dirnames, filenames) in os.walk(self.folder):
            self.images += [os.path.join(dirpath, file) for file in filenames]
        self.names = [i.split('\\')[2] for i in self.images]
        pass
    
    
    def get_encodings(self):
        for img in self.images:
            image = face_recognition.load_image_file(img)
            X_loc = [(0, image.shape[1], image.shape[0], 0)]
            self.faces.append(face_recognition.face_encodings(image, known_face_locations=X_loc)[0])
        pass
    
    
    def compare_face(self, image_to_compare):
        if image_to_compare.endswith('jpg'):
            image_to_test = face_recognition.load_image_file(image_to_compare)
        else:
            image_to_test = image_to_compare
        X_loc = [(0, image_to_test.shape[1], image_to_test.shape[0], 0)]
        image_to_test_encoding = face_recognition.face_encodings(image_to_test, known_face_locations=X_loc)[0]
        face_distances = face_recognition.face_distance(self.faces, image_to_test_encoding)
        name, dist = self.names[face_distances.argmin()], face_distances.min()
        if dist < 0.55:
            return name
        else:
            return 'Unknown'
        
        
        
folder = 'faces\\train'
fc = FaceComp(folder)
fc.compare_face("faces\\timur.jpg")





'''
This module contains class definitions
Student Class
    Name
    Student ID
    Start date in that course
    Name of Tutor
    List of assessments a tuple (ID, weight assesment, mark achieved) ( (1,40,0) zero for newly added instance to a course)

'''
from typing import List, Optional


class Student:   
    def __init__(self, name, studentID, startDate, tutorName, assessments:Optional[List[tuple]] = None):
        if assessments is None:
            assessments = list() # Initialize to empty list if not provided
        self.name = name
        self.studentID = studentID
        self.startDate = startDate
        self.tutorName = tutorName
        self.assessments = assessments

    def getName(self):
        return self.name
    def setName(self, name):
        self.name = name

    def getAssessments(self):
        return self.assessments
    def setAssessments(self, assessments:List[tuple]):
        self.assessments = assessments
    
    def addAssessment(self, assessment:tuple):
        self.assessments.append(assessment)
    
    def __str__(self):
        return f"Student(Name: {self.name}, ID: {self.studentID}, Start Date: {self.startDate}, Tutor: {self.tutorName}, Assessments: {self.assessments})"
    def __repr__(self):
        return self.__str__()
    
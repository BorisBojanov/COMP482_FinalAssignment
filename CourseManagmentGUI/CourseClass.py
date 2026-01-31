'''

This module contains class definitions

Course Class
    Name (Name of the course) "Computer Science 482: Human-Computer Interaction"
    Name Abreviated (Letters and number) "COMP 482"
    Title "Human-Computer Interaction"
    Revision number "(Rev 7)"
    date of initial offering "01/09/2025"
    list of students (instances of Student class)
    Professor name
    List of assessment items a tuple of (ID, name, weight) in which:
        ID: assessment item ID; 1,2,3
        name: assessment name; Assignment 1 or Final Exam
        weight: is percentage of the assessment towards final grade; 40, 60

'''

from typing import List, Optional
from StundentClass import Student

class Course:
    def __init__(self, 
                name, 
                nameAbreviated, 
                title, 
                revisionNumber, 
                dateOffered, 
                professorName,
                students:Optional[List[Student]]=None, 
                assessments:Optional[List[tuple]] = None 
            ):
        
        self.name = name
        self.nameAbreviated = nameAbreviated
        self.title = title
        self.revisionNumber = revisionNumber
        self.date = dateOffered
        self.professorName = professorName
        self.assessments: List[tuple] = []
        self.filepath: Optional[str] = None
        self.registeredStudents: List[Student] = []

        # list of Student instances
        if students is not None: #students leaking between courses
            self.registeredStudents = students
        else:
            self.registeredStudents = []

        # list of tuples (ID, name, weight)
        if assessments is not None: #assessments leaking between courses
            self.assessments = assessments
        else:
            self.assessments = []

    
'''
The CourseManagmentGUI, GUI application should meet the following criteria:
TODO:
a.  There should be a button for adding a new course to the system, 
    which will open a form for input and save basic course info previously mentioned, 
    with the list of students empty. 

    Note that when saving the basic course info, 
    the system should be able to check whether the total weight of all assessment items make up 100%.
    DONE
b.  new course is added to the system, 
    Create a unique binary file for permanent storage of the course data.
    DONE
c.  At the start of the system, 
    the system should automatically load all courses from their respective binary files 
    to restore their internal object representation.
    DONE
d. There should be a button to get a list of courses being offered to students.
    DONE
e. The user should be able to select a course from the list.
    Done
f. The user should be able to add students to the selected course.
    Done
g. The user should be to see a list of students in the course.
    Done
h. The user should be able to select a student from the list.
    Done
i. The user should be able to record an assessment for the selected student.
    Done
j. The system should automatically calculate display the final grade of the student for the course.
    Done
k. The user should be able to see a list of assessments, including the calculated final grade for the selected student. 
    Done
l. There should be a button to shut down the system, but before shutting down the application, the system must save/pickle the data for each course back to its binary file.
    Done


4. (5 marks) Your analysis and design of the system should be well documented in your assignment
report.
    
    
5. (5 marks) Within each of your program files, there should be a docstring at the beginning stating the
name and purpose of the file, as well as the ownership and revision history. One docstring is
required for each class and function/method class. End-of-line comments are desired when deemed
necessary.


IDEA
TODO: Make the GUI show in the bottom of the window, which course and student and or assessment is selected currently.
'''




import tkinter as tk
from tkinter import messagebox
import CourseClass as cdef
import os
import pickle
import uuid
import re
import datetime


class CourseManagementGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Course Management System")
        self.root.geometry("400x200")

        # Student fields
        self.studentNameEntry = tk.Entry()
        self.studentIDEntry = tk.Entry()
        self.startDateEntry = tk.Entry()
        self.tutorNameEntry = tk.Entry()

        # Assessments state
        self.assessments = []
        self.totalWeight = tk.IntVar(value=0)
        self.statusVariable = tk.StringVar(value="Add assessments until total = 100%.")
        self.assessmentIDEntry = tk.StringVar(value="")  # Assignment1_20 ID pattern


        self.frame = tk.Frame(self.root)
        self.frame.grid(padx=10, pady=10)
        
        self.courses = self.loadCourses()
        self.registeredStudents = []
        
        self.selectedStudent = None
        self.selectedStudentIndex = None

        self.selectedCourse = None
        self.selectedCourseIndex = None

        self.submitableForm = False
        self.root.protocol("WM_DELETE_WINDOW", self.shutDown)

        self.mainMenu()

    # setup data directory to be relative to this script
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIRECTORY = os.path.join(BASE_DIR, "courseData")

    # widget helpers 
    # Note, Positional args first. Once *args or **kwargs appears, everything must be named.
    # Create explicit groups of keword args 
    def createButton(self, parent, text, command,*,grid=None,font=None, **kwargs):
        btn = tk.Button(parent, text=text, command=command)
        if grid:
            btn.grid(**grid)
        if font:
            btn.config(font=font)
        if kwargs:
            btn.config(**kwargs)
        return btn

    def createLabel(self, parent, text, *, grid=None, font=None, **kwargs):
        lbl = tk.Label(parent, text=text)
        if grid:
            lbl.grid(**grid)
        if font:
            lbl.config(font=font) # font=("Arial", 11, "bold")
        if kwargs:
            lbl.config(**kwargs)
        return lbl

    def createEntry(self, parent,*, grid=None, font=None, **kwargs):
        # widget options like width, textvariable, show
        ent = tk.Entry(parent)

        '''class Grid
        column=number - use cell identified with given column (starting with 0)
        columnspan=number - this widget will span several columns
        in=master - use master to contain this widget
        in_=master - see 'in' option description
        ipadx=amount - add internal padding in x direction
        ipady=amount - add internal padding in y direction
        padx=amount - add padding in x direction
        pady=amount - add padding in y direction
        row=number - use cell identified with given row (starting with 0)
        rowspan=number - this widget will span several rows
        sticky=NSEW - if cell is larger on which sides will this
                      widget stick to the cell boundary
        '''
        if grid:
            ent.grid(**grid)
        if font:
            ent.config(font=font)
        if kwargs:
            ent.config(**kwargs)
        return ent

    def createTextArea(self, parent, width=40, height=10, *, grid=None, font=None, **kwargs):
        txt = tk.Text(parent, width=width, height=height)
        if grid:
            txt.grid(**grid)
        if font:
            txt.config(font=font)
        if kwargs:
            txt.config(**kwargs)
        return txt

    # Listbox stores strings, not objects.
    # we keep a parallel Python list (students) in the same order you insert items, then
    def createListbox(self, parent, width=40, height=10, listvariable=None, *, grid=None, font=None, **kwargs):
        '''
        Docstring for createListbox
        
        :param self: Description
        :param parent: Description
        :param width: Description
        :param height: Description
        :param listvariable: Description
        :param grid: Description
        :param font: Description
        :param kwargs: Description
        '''
        if listvariable is None:
            listvariable = tk.StringVar(value=[])

        lst = tk.Listbox(parent, width=width, height=height, listvariable=listvariable)
        lst.listvariable = listvariable  # KEEP REFERENCE        
        
        if grid:
            lst.grid(**grid)
        if font:
            lst.config(font=font)
        if kwargs:
            lst.config(**kwargs)
        return lst

    def createFormEntry(self, parent, labelText, row, **kwargs):
        """
        Helper to create a Label and an Entry in a standard form layout.
        Label is placed in column 0, Entry in column 1.
        """
        self.createLabel(parent, labelText, grid={"column": 0, "row": row, "sticky": "w"})
        return self.createEntry(parent, grid={"column": 1, "row": row, "sticky": "ew"}, **kwargs)


    def changeCourseBinAttribute(self, courseObj:cdef.Course, NEWattribute:str, OLDattribute:str, filepath ,newValue):
            # ---- MIGRATION: old -> new attribute name ----
            if hasattr(courseObj, OLDattribute) and not hasattr(courseObj, NEWattribute):
                setattr(courseObj, NEWattribute, getattr(courseObj, OLDattribute))
                delattr(courseObj, OLDattribute)
                NEWattribute = OLDattribute
                # re-save so next run is clean
                with open(filepath, "wb") as f:
                    pickle.dump(courseObj, f)

                courseObj.filepath = filepath # store filepath in object for future use
                print(f"Migrated {OLDattribute} to {NEWattribute} in {filepath}")
            return courseObj

    # file loading and saving methods
    def checkDataDirectory(self):
        os.makedirs(self.DATA_DIRECTORY, exist_ok=True)

    def safeafyFileName(self, name:str):
        name = name.strip()

        # \s : find whitespace
        # +  :and one or more
        name = re.sub(r"\s+", "_", name)

        # [sutuff] : match any character in stuff between brackets
        # ^ : negation or not
        # A-Z: all uppercase letters
        # a-z: all lowercase letters
        # 0-9: all digits
        # _: underscores
        # \-: hyphens (escaped with backslash)
        # Remove everry character that is not a letter or number or underscore or hyphen
        # https://www.w3schools.com/python/python_regex.asp
        name = re.sub(r"[^A-Za-z0-9_\-]", "", name)

        # if name is empty, generate a uuid as name
        if not name:
            name = "course_" + str(uuid.uuid4())
        return name

    def courseFilename(self, courseObj:cdef.Course):
        # filename with a uuid to avoid douplicates
        name = self.safeafyFileName(courseObj.nameAbreviated)
        rev = self.safeafyFileName(courseObj.revisionNumber)
        date = self.safeafyFileName(courseObj.date.replace("/", "-"))
        filename = f"{name}_{rev}_{date}.bin"
        return filename


    # When a new course, save to unique binary file
    def saveCourseToFile(self, courseObj:cdef.Course):
        self.checkDataDirectory()
        filename = self.courseFilename(courseObj)
        filepath = os.path.join(self.DATA_DIRECTORY, filename)

        with open(filepath, "wb") as f:
            pickle.dump(courseObj, f)
        
        courseObj.filepath = filepath
        return filepath

    # convert old objects as they load, then re-save them
    def loadCourses(self):
        self.checkDataDirectory()
        loadedCourses = []

        for name in os.listdir(self.DATA_DIRECTORY):
            if name.endswith(".bin"):
                filepath = os.path.join(self.DATA_DIRECTORY, name)
                
                try:
                    with open(filepath, "rb") as f:
                        courseObj = pickle.load(f)
                        courseObj.filepath = filepath  # track where it came from
                        loadedCourses.append(courseObj)

                except Exception as e:
                    print(f"Error loading {filepath}: {e}")

        return loadedCourses

    def saveSelectedCourse(self):
        if not self.selectedCourse:
            return
        filepath = getattr(self.selectedCourse, "filepath", None)
        if filepath:
            with open(filepath, "wb") as f:
                pickle.dump(self.selectedCourse, f)
        else:
            # fallback: treat it like a new course
            self.saveCourseToFile(self.selectedCourse)


    def saveAllCourses(self):
        """
        loop through all self.courses
        pickles each course back to its binary file. 
        If a course doesn't have a filepath yet using saveCourseToFile().
        """
        for course in self.courses:
            filepath = getattr(course, "filepath", None)

            # If the course came from disk, it should already have filepath (you set this in loadCourses()).
            if filepath:
                with open(filepath, "wb") as f:
                    pickle.dump(course, f)
            else:
                # Course has no known filepath yet -> treat like new and create a file
                self.saveCourseToFile(course)

    def shutDown(self):
        """
        shutDown process for the Quit button and window close event.
        """
        if not messagebox.askyesno("Exit","Save all courses and exit?"):
            return

        try:
            self.saveAllCourses()
            messagebox.showinfo("Saved","Courses saved successfully.")
            self.root.destroy() # now exit
        except Exception as e:
            messagebox.showerror("Error",f"Something went wrong while saving courses: {e}")
            return



    # Course management methods
    def newCourseForm(self):
        # Use Toplevel (NOT another Tk())
        self.newCourseWindow = tk.Toplevel(self.root)
        self.newCourseWindow.title("New Course Form Window")
        self.newCourseWindow.geometry("520x420")

        self.newCourseFrame = tk.Frame(self.newCourseWindow)
        self.newCourseFrame.grid(padx=10, pady=10, sticky="nw")

        r = 0
        self.createLabel(self.newCourseFrame, "New Course Form", grid={"column": 0, "row": r})
        r += 1

        # Course fields
        self.courseNameEntry = self.createFormEntry(self.newCourseFrame, "Course Name:", r)
        r += 1

        self.courseAbbrevEntry = self.createFormEntry(self.newCourseFrame, "Course Abbreviated Name:", r)
        r += 1

        self.courseTitleEntry = self.createFormEntry(self.newCourseFrame, "Course Title:", r)
        r += 1

        self.courseRevisionEntry = self.createFormEntry(self.newCourseFrame, "Revision Number:", r)
        r += 1

        self.courseDateEntry = self.createFormEntry(self.newCourseFrame, "Date Offered:", r)
        r += 1

        self.professorNameEntry = self.createFormEntry(self.newCourseFrame, "Professor Name:", r)
        r += 1

        # Registered students empty for now (per assignment)
        self.registeredStudents = []

        # Assessments state
        self.assessments = []
        self.totalWeight = tk.IntVar(value=0)
        self.statusVariable = tk.StringVar(value="Add assessments until total = 100%.")
        self.assessmentIDEntry = tk.StringVar(value="")  # default ID pattern

        # Assessment input area
        r += 1
        self.createLabel(self.newCourseFrame, "Assessments", grid={"column": 0, "row": r})
        r += 1

        self.assessmentNameEntry = self.createFormEntry(self.newCourseFrame, "Assessment Name:", r)
        r += 1

        self.assessmentWeightEntry = self.createFormEntry(self.newCourseFrame, "Assessment Weight (%):", r)
        r += 1

        # Total + status
        self.createLabel(self.newCourseFrame, "Total Weight:", grid={"column": 0, "row": r})
        tk.Label(self.newCourseFrame, textvariable=self.totalWeight).grid(column=1, row=r, sticky="w")
        r += 1

        tk.Label(self.newCourseFrame, textvariable=self.statusVariable).grid(column=0, row=r, columnspan=2, sticky="w")
        r += 1

        # Buttons
        self.addAssessmentButton = self.createButton(
            self.newCourseFrame,
            "Add Assessment",
            self.addAssessment,
            grid={"column": 0, "row": r, "pady": 10, "sticky": "w"}
        )

        self.submitButton = self.createButton(
            self.newCourseFrame,
            "Submit Course",
            self.submitNewCourse,
            grid={"column": 1, "row": r, "pady": 10, "sticky": "w"}
        )

        self.submitButton.config(state="disabled")  # until total == 100

        # Optional: show assessments list
        r += 1
        self.createLabel(self.newCourseFrame, "Assessments Added:", grid={"column": 0, "row": r})
        self.assessmentsListbox = self.createListbox(self.newCourseFrame, width=50, height=5, grid={"column": 0, "row": r + 1, "columnspan": 2, "sticky": "w"})
        
        self.computeTotal()

    def computeTotal(self):
        total = sum(w for (_aid, _aname, w) in self.assessments)
        self.totalWeight.set(total)

        if total < 100:
            self.statusVariable.set(f"Need {100 - total}% more to reach 100%.")
            self.submitButton.config(state="disabled")
            self.addAssessmentButton.config(state="normal")
        elif total == 100:
            self.statusVariable.set("Total is 100%. You can submit now.")
            self.submitButton.config(state="normal")
            self.addAssessmentButton.config(state="disabled")
        else:
            # If you ever allow over-100, you can adjust this logic.
            self.statusVariable.set(f"Total is {total}%. Too high—fix weights.")
            self.submitButton.config(state="disabled")
            self.addAssessmentButton.config(state="normal")

    def addAssessment(self):
        assessmentIDText = self.assessmentIDEntry.get().strip()
        assessmentName = self.assessmentNameEntry.get().strip()
        weightText = self.assessmentWeightEntry.get().strip()
        abbreviatedCourseName = self.courseAbbrevEntry.get().strip()

        if not assessmentName or not weightText:
            messagebox.showerror("Missing data", "Enter Assessment Name and Weight.")
            self.submitableForm = False
            return

        try:
            assessmentIDText = abbreviatedCourseName + "_" + assessmentName + "_" + weightText
            
            print(self.safeafyFileName(assessmentIDText))
            assessmentID = self.safeafyFileName(assessmentIDText)
        except ValueError:
            messagebox.showerror("Invalid ID", "Assessment ID must be a number (e.g., 1).")
            self.submitableForm = False
            return
        try:
            weight = int(weightText)
        except ValueError:
            messagebox.showerror("Invalid weight", "Weight must be an integer (e.g., 10).")
            self.submitableForm = False
            return

        if weight <= 0:
            messagebox.showerror("Invalid weight", "Weight must be greater than 0.")
            self.submitableForm = False
            return

        current_total = sum(x[2] for x in self.assessments)
        if current_total + weight > 100:
            messagebox.showerror(
                "Too much weight",
                f"That would make the total {current_total + weight}%, exceeding 100%."
            )
            self.submitableForm = False
            return

        self.assessments.append((assessmentID, assessmentName, weight))
        self.assessmentsListbox.insert(tk.END, f"{assessmentID} | {assessmentName} | {weight}%")

        # clear inputs
        self.assessmentNameEntry.delete(0, tk.END)
        self.assessmentWeightEntry.delete(0, tk.END)

        self.computeTotal()

    def submitNewCourse(self):
        if self.totalWeight.get() != 100:
            messagebox.showerror("Cannot submit", "Total assessment weight must equal 100%.")
            return

        # Pull form values
        courseName = self.courseNameEntry.get().strip()
        courseAbrev = self.courseAbbrevEntry.get().strip()
        courseTitle = self.courseTitleEntry.get().strip()
        revision = self.courseRevisionEntry.get().strip()
        dateOffered = self.courseDateEntry.get().strip()
        professor = self.professorNameEntry.get().strip()

        if not courseName:
            messagebox.showerror("Missing data", "Course Name is required.")
            return
        if not courseAbrev:
            messagebox.showerror("Missing data", "Course Abbreviated Name is required.")
            return
        if not courseTitle:
            messagebox.showerror("Missing data", "Course Title is required.")
            return
        if not revision:
            messagebox.showerror("Missing data", "Revision Number is required.")
            return
        if not dateOffered:
            messagebox.showerror("Missing data", "Date Offered is required.")
            return


        # Create Course object
        # name, nameAbreviated, title, revisionNumber, dateOffered, professorName, students:Optional[List[Student]]=None, assessments:Optional[List[tuple]] = None 
        courseObj = cdef.Course(
            name = courseName,
            nameAbreviated = courseAbrev,
            title = courseTitle,
            revisionNumber = revision,
            dateOffered = dateOffered,
            professorName = professor,
            students = self.registeredStudents,
            assessments = self.assessments
        )

        self.courses.append(courseObj)

        # save to unique binary file here
        savedPath = self.saveCourseToFile(courseObj)
        print(f"Course saved to {savedPath}")

        messagebox.showinfo("Success", f"Course '{courseName}' submitted! \n Saved to: {savedPath}")
        self.newCourseWindow.destroy()

    
    def showCourseList(self):
                # Read the selected row index from the Listbox, 
        # then use that index to grab the correct Course object from self.courses.
        def confirmSelection(event=None):
            selection = listbox.curselection() # tuple of indices
            if not selection:
                messagebox.showwarning("No selection", "Please select a course first.")
                return

            idx = selection[0]  # 0-based index
            self.selectedCourseIndex = idx
            self.selectedCourse = self.courses[idx]

            messagebox.showinfo(
                "Course Selected",
                f"Selected: {self.selectedCourse.nameAbreviated} - {self.selectedCourse.title}"
            )
            # window.destroy()

        def select(event=None):
            # called everytime a selcetion is made    
            if listbox.curselection():
                selectButton.config(state="normal")
            else:
                selectButton.config(state="disabled")
        
        courses = self.courses

        if not courses:
            messagebox.showinfo("No courses", "No courses available to display.")
            
        
        window = tk.Toplevel(self.root)
        window.title("Courses Available")
        window.geometry("400x300")
        
        frame = tk.Frame(window)
        frame.grid(padx=10, pady=10)
        titleLabel = self.createLabel(
            frame, 
            "Select a course from the list:", 
            grid={"row": 0, "column": 0, "columnspan": 2, "sticky": "w"}
        )

        listbox = self.createListbox(
            frame, 
            width=50, 
            height=10, 
            grid={"row": 1, "column": 0, "columnspan": 2, "sticky": "w"},
            exportselection=False   # keeps selection even when focus changes
        )

        # populate listbox 
        for index, course in enumerate(courses, start=1):
            # create a list containing all course objects as pretty strings, assuming createListbox is setup to take a listvariable
            
            # Simple way to add to list box
            listbox.insert(tk.END, f"{index}. {course.nameAbreviated} - {course.title} (REV {course.revisionNumber})")

        # Select Button
        selectButton = self.createButton(
            frame, 
            "Select", 
            confirmSelection, 
            grid={"row": 2, "column": 0, "pady": 10, "sticky": "ew"}
        )

        # Select button disabled until something is clicked
        listbox.bind("<<ListboxSelect>>", select)
        listbox.bind("<Double-Button-1>", confirmSelection)

                
        # Add New Course Button
        newCourse = self.createButton(
            frame,
            "Add New Course",
            self.newCourseForm,
            grid={ "row": 3, "column": 0, "pady": 10, "sticky": "w"}
        )
        newCourse

        # Show list of students in selected course
        listStudents = self.createButton(
            frame,
            "List Students (Selected Course)",
            self.showStudentList,
            grid={"row": 3,"column": 1, "pady": 10, "sticky": "w"}
        )

    # Student management methods
    def addStudentForm(self, window, object, **kwargs):
        
    def addStudentForm(self):
        def submit():
            name = self.studentNameEntry.get().strip()
            studentID = self.studentIDEntry.get().strip()
            start = self.startDateEntry.get().strip()
            tutor = self.tutorNameEntry.get().strip()

            if not name or not studentID or not start or not tutor:
                messagebox.showerror("Missing data", "Fill in all fields.")
                return
            
            # prevent duplicate student IDs in a course
            for student in self.selectedCourse.registeredStudents:
                if student.studentID == studentID:
                    messagebox.showerror("Duplicate ID", f"Student ID {studentID} already exists in this course.")
                    return
            
            # student assessments from course assessments:
            # course: (ID, name, weight) -> student: (ID, weight, 0)
            studentAssessments = []
            for (assessmentID, assessmentName, weight) in self.selectedCourse.assessments:
                studentAssessments.append( (assessmentID, weight, 0) ) # 0 for newly added student
            
            # Create Student object
    
            student = cdef.Student(
                name=name,
                studentID=studentID,
                startDate=start,
                tutorName=tutor,
                assessments=studentAssessments
            )

            self.selectedCourse.registeredStudents.append(student)
            self.saveSelectedCourse()
            messagebox.showinfo("Success", f"Student '{name}' added to course '{self.selectedCourse.nameAbreviated}'.")
            
            window.destroy()
    
        if self.selectedCourse is None:
            messagebox.showwarning("No course selected", "Please select a course first.")
            return

        window = tk.Toplevel(self.root)
        window.title("add Student ")
        window.geometry("400x300")

        frame = tk.Frame(window)
        frame.grid(padx=10, pady=10, sticky="nw")
        r = 0

        self.createLabel(frame, f"Add A Student to :{self.selectedCourse.nameAbreviated}", grid={"column": 0, "row": r}, font=("Arial", 11, "bold"))
        r += 1
        # Student fields
        self.studentNameEntry = self.createFormEntry(frame, "Student Name:", r)
        r += 1
        self.studentIDEntry = self.createFormEntry(frame, "Student ID:", r)
        r += 1
        self.startDateEntry = self.createFormEntry(frame, "Start Date (DD/MM/YYYY):", r)
        r += 1
        self.tutorNameEntry = self.createFormEntry(frame, "Tutor Name:", r)
        r += 1


        self.createButton(
            frame,
            "Add a Student",
            submit,
            grid={"column": 0, "row": r, "pady": 10, "sticky": "w"}
        )

    def showStudentList(self):
        def select(event=None):
            if listbox.curselection():
                selectButton.config(state="normal")
            else:
                selectButton.config(state="disabled")
        def confirmSelection(event=None):
            selection = listbox.curselection()
            if not selection:
                messagebox.showwarning("No selection", "Please select a student first.")
                return

            idx = selection[0]  # 0-based
            self.selectedStudentIndex = idx
            self.selectedStudent = students[idx]

            messagebox.showinfo(
                "Student Selected",
                f"Selected: {self.selectedStudent.name} ({self.selectedStudent.studentID})"
            )

            # optional: keep window open, or close it
            # window.destroy()
        
        selectedCourse = self.selectedCourse

        # Must have a selected course first
        if selectedCourse is None:
            messagebox.showwarning("No course selected", "Select a course first.")
            return
        
        students = selectedCourse.registeredStudents  # list of Student objects
        
        # Course uses registeredStudents
        if not students:
            messagebox.showinfo("No students", "This course has no students yet.")
            

        window = tk.Toplevel(self.root)
        window.title("Students in Selected Course")
        window.geometry("560x340")

        frame = tk.Frame(window)
        frame.grid(padx=10, pady=10, sticky="nsew")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        self.createLabel(
            frame,
            f"Students in: {self.selectedCourse.nameAbreviated} - {self.selectedCourse.title}",
            grid={"row": 0, "column": 0, "columnspan": 2, "sticky": "w"},
            font=("Arial", 11, "bold")
        )

        listbox = self.createListbox(
            frame,
            width=70,
            height=10,
            grid={"row": 1, "column": 0, "columnspan": 2, "sticky": "nsew"},
            exportselection=False
        )

        # Populate listbox: listbox index == students list index
        for s in students:
            # Student has name, studentID, startDate, tutorName
            listbox.insert(tk.END, f"{s.studentID} | {s.name} | Start: {s.startDate} | Tutor: {s.tutorName}")

        # Select button disabled until something is clicked
        selectButton = self.createButton(
            frame,
            "Select Student",
            lambda: confirmSelection(),
            grid={"row": 2, "column": 0, "pady": 10, "sticky": "ew"},
            state="disabled"
        )
        cancelButton = self.createButton(
            frame,
            "Close",
            window.destroy,
            grid={"row": 2, "column": 1, "pady": 10, "sticky": "ew"}
        )
                # Add Student
        
        self.createButton(
            frame,
            "Add Student to Selected Course",
            self.addStudentForm,
            grid={"column": 0, "row": 3, "pady": 8, "padx": 10, "sticky": "w"}
        )

        listbox.bind("<<ListboxSelect>>", select)
        listbox.bind("<Double-Button-1>", confirmSelection)

    # Assessment management methods
    # calculate final grade for selected student
    def calculateFinalGrade(self, student):
        """
        student.assessments list[tuples]: [(assessmentID, weight, mark)]
        where mark is 0..100 (percent score for that assessment item)
        final grade = sum( (mark/100) * weight ) over all items
        """
        total = 0.0
        for (_aid, weight, mark) in student.assessments:
            total += (mark / 100.0) * weight
        return round(total, 2)

    # record assessment for selected student in selected course
    def recordAssessmentForm(self):
        # Must have a selected course + selected student
        if self.selectedCourse is None:
            messagebox.showwarning("No course selected", "Select a course first.")
            return
        if self.selectedStudent is None:
            messagebox.showwarning("No student selected", "Select a student first.")
            return

        win = tk.Toplevel(self.root)
        win.title("Record Assessment Mark")
        win.geometry("560x360")

        frame = tk.Frame(win)
        frame.grid(padx=10, pady=10, sticky="nsew")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(2, weight=1)

        self.createLabel(
            frame,
            f"Student: {self.selectedStudent.name} ({self.selectedStudent.studentID})",
            grid={"row": 0, "column": 0, "columnspan": 2, "sticky": "w"},
            font=("Arial", 11, "bold")
        )

        # List assessments for this student
        self.createLabel(frame, "Select assessment:", grid={"row": 1, "column": 0, "sticky": "w"})
        listbox = self.createListbox(
            frame,
            width=70,
            height=10,
            grid={"row": 2, "column": 0, "columnspan": 2, "sticky": "nsew"},
            exportselection=False
        )

        # map from assessmentID -> assessment_name (from course)
        assessmentDictByID = {aid: aname for (aid, aname, _w) in self.selectedCourse.assessments}

        # Fill listbox from student.assessments (id, weight, mark)
        for (aid, weight, mark) in self.selectedStudent.assessments:
            aname = assessmentDictByID.get(aid, f"Assessment {aid}")
            listbox.insert(tk.END, f"ID {aid} | {aname} | Weight {weight}% | Mark {mark}%")

        self.createLabel(frame, "Enter mark (0-100):", grid={"row": 3, "column": 0, "sticky": "w"})
        mark_entry = self.createEntry(frame, grid={"row": 3, "column": 1, "sticky": "w"})
        mark_entry = self.createFormEntry(frame, "Enter mark (0-100):", 3)

        save_btn = self.createButton(
            frame, "Save Mark", lambda: saveMark(),
            grid={"row": 4, "column": 0, "pady": 10, "sticky": "ew"},
            state="disabled"
        )
        self.createButton(
            frame, "Cancel", win.destroy,
            grid={"row": 4, "column": 1, "pady": 10, "sticky": "ew"}
        )

        def onSelect(event=None):
            save_btn.config(state="normal" if listbox.curselection() else "disabled")

        def saveMark():
            selection = listbox.curselection()
            if not selection:
                messagebox.showwarning("No selection", "Select an assessment first.")
                return

            # validate mark
            text = mark_entry.get().strip()
            try:
                mark = float(text)
            except ValueError:
                messagebox.showerror("Invalid mark", "Enter a number between 0 and 100.")
                return
            if mark < 0 or mark > 100:
                messagebox.showerror("Invalid mark", "Mark must be between 0 and 100.")
                return

            idx = selection[0]  # index into student.assessments
            aid, weight, _old_mark = self.selectedStudent.assessments[idx]

            # Update tuple (tuples are immutable, replace it)
            self.selectedStudent.assessments[idx] = (aid, weight, mark)

            # Persist the updated course (so it saves after restart)
            self.saveSelectedCourse()

            finalGrade = self.calculateFinalGrade(self.selectedStudent)
            messagebox.showinfo("Saved", f"Saved mark for assessment {aid}.\nFinal grade now: {finalGrade}%")

            win.destroy()

        listbox.bind("<<ListboxSelect>>", onSelect)

    # show assessments and final grade for selected student
    def showStudentAssessments(self):
        if self.selectedCourse is None:
            messagebox.showwarning("No course selected", "Select a course first.")
            return
        if self.selectedStudent is None:
            messagebox.showwarning("No student selected", "Select a student first.")
            return

        window = tk.Toplevel(self.root)
        window.title("Assessments + Final Grade")
        window.geometry("600x360")

        frame = tk.Frame(window)
        frame.grid(padx=10, pady=10, sticky="nsew")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(2, weight=1)

        finalGrade = self.calculateFinalGrade(self.selectedStudent)

        self.createLabel(
            frame,
            f"Student: {self.selectedStudent.name} ({self.selectedStudent.studentID})",
            grid={"row": 0, "column": 0, "sticky": "w"},
            font=("Arial", 11, "bold")
        )

        self.createLabel(
            frame,
            f"Final Grade: {finalGrade}%",
            grid={"row": 1, "column": 0, "sticky": "w"},
            font=("Arial", 11, "bold")
        )

        listbox = self.createListbox(
            frame,
            width=75,
            height=12,
            grid={"row": 2, "column": 0, "sticky": "nsew"},
            exportselection=False
        )

        assessmentDictByID = {aid: aname for (aid, aname, _w) in self.selectedCourse.assessments}

        # Display each assessment line
        for (aid, weight, mark) in self.selectedStudent.assessments:
            aname = assessmentDictByID.get(aid, f"Assessment {aid}")
            contribution = round((mark / 100.0) * weight, 2)
            listbox.insert(tk.END, f"ID {aid} | {aname} | Weight {weight}% | Mark {mark}% | Contribution {contribution}%")

        self.createButton(frame, "Close", window.destroy, grid={"row": 3, "column": 0, "pady": 10, "sticky": "e"})



    # main window 
    def mainMenu(self):
        # Title label
        self.createLabel(
            self.frame, 
            "Course Management System", 
            grid={"column": 0, "row": 0},
            font=("Arial", 11, "bold")
        )

        # Buttons
        # List Courses
        self.createButton(
            self.frame,
            "Show List of Courses",
            self.showCourseList,
            grid={"column": 0, "row": 1, "pady": 8, "sticky": "w"}
        )

        self.createButton(
            self.frame,
            "Record Assessment (Selected Student)",
            self.recordAssessmentForm,
            grid={"column": 0, "row": 4, "pady": 8, "sticky": "w"}
        )

        self.createButton(
            self.frame,
            "View Assessments + Final Grade",
            self.showStudentAssessments,
            grid={"column": 0, "row": 5, "pady": 8, "sticky": "w"}
        )

        # Quit
        self.createButton(
            self.frame,
            "Quit",
            self.shutDown,
            grid={"column": 1, "row": 1, "pady": 8, "padx": 10, "sticky": "w"}
        )

        
    # run the app 
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = CourseManagementGUI()
    app.run()
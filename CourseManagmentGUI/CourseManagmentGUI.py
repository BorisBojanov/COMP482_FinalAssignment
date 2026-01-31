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
from typing import Optional, List
import CourseClass as CourseClass
import StundentClass as StudentClass
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
        
        self._listbox_variables = {}

        self.courses = self.loadCourses()
        self.registeredStudents: List = []
        
        self.selectedStudent = StudentClass.Student("", "", "", "")
        self.selectedStudentIndex = int(0)
        self.selectedCourse = CourseClass.Course("", "", "", "", "", "", [], [])
        self.selectedCourseIndex = int(0)

        # Form Entry Widets
        self.courseNameEntry = str()
        self.courseAbbrevEntry = str()
        self.courseTitleEntry = str()
        self.courseRevisionEntry = str()
        self.courseDateEntry = str()
        self.submitButton = tk.Button()
        self.addAssessmentButton = tk.Button()
        self.professorNameEntry = str()

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
        # Create Listbox without listvariable if None (Listbox will manage its own internal variable)
        if listvariable is None:
            lst = tk.Listbox(parent, width=width, height=height)
        else:
            lst = tk.Listbox(parent, width=width, height=height, listvariable=listvariable)
            lst.listvariable = listvariable  # type: ignore  # KEEP REFERENCE
        
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

    """
    Form Builder
    This module provides a flexible, reusable form creation method for CourseManagementGUI.

    PATTERN :
    Common elements across addStudentForm, newCourseForm, and recordAssessmentForm:
    1. Create Toplevel window with title and geometry
    2. Create Frame with padding
    3. Add title label (optional, with bold font)
    4. Create form fields using createFormEntry (label + entry pairs)
    5. Add additional widgets (listboxes, status labels, etc.)
    6. Add action buttons (submit, cancel, etc.)
    7. Define submit callback with validation logic

    DESIGN:
    The addForm method accepts:
    - title: Window title
    - geometry: Window size (e.g., "400x300")
    - form_title: Optional form header text
    - fields: List of field configurations
    - widgets: Optional additional widgets to insert
    - buttons: List of button configurations
    - submit_callback: Function to call on form submission
    - validation_callback: Optional pre-submission validation

    """
    def addForm(self, 
                title="Form", 
                geometry="400x300",
                form_title=None,
                fields=None,
                additional_widgets=None,
                buttons=None,
                on_submit=None,
                preconditions=None):
        """
        Create a reusable form with configurable fields and buttons.
        
        Parameters:
        -----------
        title : str
            Window title
        geometry : str
            Window size (e.g., "400x300")
        form_title : str, optional
            Bold header text at top of form
        fields : list of dict
            Each dict contains:
            - 'label': str - Label text for the field
            - 'name': str - Attribute name to store the Entry widget
            - 'default': str, optional - Default value
            - 'widget_type': str, optional - 'entry' (default), 'listbox', 'label'
            - 'widget_options': dict, optional - Additional widget kwargs
        additional_widgets : list of dict, optional
            Custom widgets to add at specific rows:
            - 'type': 'label', 'listbox', 'button', etc.
            - 'row': int - Row position
            - 'name': str - Attribute name to store widget reference
            - 'config': dict - Widget configuration
        buttons : list of dict
            Each dict contains:
            - 'text': str - Button text
            - 'command': callable - Button callback
            - 'column': int - Grid column (default 0)
            - 'state': str, optional - Button state
        on_submit : callable, optional
            Callback function when form is submitted
            Receives dict of {field_name: value}
        preconditions : callable, optional
            Function to check before showing form
            Should return (bool, str) - (is_valid, error_message)
        
        Returns:
        --------
        dict containing:
            - 'window': Toplevel window reference
            - 'frame': Frame reference
            - 'widgets': dict of all created widgets by name
        
        Example Usage:
        --------------
        # Simple student form
        form_config = {
            'title': 'Add Student',
            'geometry': '400x300',
            'form_title': 'Add A Student to: COMP482',
            'fields': [
                {'label': 'Student Name:', 'name': 'studentName'},
                {'label': 'Student ID:', 'name': 'studentID'},
                {'label': 'Start Date (DD/MM/YYYY):', 'name': 'startDate'},
                {'label': 'Tutor Name:', 'name': 'tutorName'}
            ],
            'buttons': [
                {'text': 'Submit', 'command': lambda: submit_student(form_refs)},
                {'text': 'Cancel', 'command': lambda: form_refs['window'].destroy(), 'column': 1}
            ]
        }
        form_refs = self.addForm(**form_config)
        """
        
        # Check preconditions
        if preconditions:
            is_valid, error_msg = preconditions()
            if not is_valid:
                messagebox.showwarning("Precondition Failed", error_msg)
                return None
        
        # Create window
        window = tk.Toplevel(self.root)
        window.title(title)
        window.geometry(geometry)

        # Create frame
        frame = tk.Frame(window)
        frame.grid(padx=10, pady=10, sticky="nw")
        
        row = 0
        widgets = {}
        
        # Add form title if provided
        if form_title:
            title_label = self.createLabel(
                frame, 
                form_title, 
                grid={"column": 0, "row": row, "columnspan": 2, "sticky": "w"},
                font=("Arial", 11, "bold")
            )
            widgets['_title_label'] = title_label
            row += 1
        
        # Create form fields
        if fields:
            for field_config in fields:
                label_text = field_config['label']
                field_name = field_config['name']
                widget_type = field_config.get('widget_type', 'entry')
                default = field_config.get('default', '')
                widget_options = field_config.get('widget_options', {})
                
                if widget_type == 'entry':
                    entry = self.createFormEntry(frame, label_text, row, **widget_options)
                    if default:
                        entry.insert(0, default)
                    widgets[field_name] = entry
                    setattr(self, f"{field_name}Entry", entry)
                
                elif widget_type == 'label':
                    label = self.createLabel(
                        frame, 
                        label_text, 
                        grid={"column": 0, "row": row, "sticky": "w"},
                        **widget_options
                    )
                    widgets[field_name] = label
                
                elif widget_type == 'listbox':
                    self.createLabel(frame, label_text, grid={"column": 0, "row": row, "sticky": "w"})
                    row += 1
                    listbox = self.createListbox(
                        frame,
                        grid={"column": 0, "row": row, "columnspan": 2, "sticky": "nsew"},
                        **widget_options
                    )
                    widgets[field_name] = listbox
                    setattr(self, f"{field_name}Listbox", listbox)
                
                row += 1
        
        # Add additional custom widgets
        if additional_widgets:
            for widget_config in additional_widgets:
                wtype = widget_config['type']
                wrow = widget_config.get('row', row)
                wname = widget_config['name']
                wconfig = widget_config.get('config', {})
                widget = type(tk)
                if wtype == 'label':
                    widget = self.createLabel(frame, **wconfig, grid={**wconfig.get('grid', {}), 'row': wrow})
                elif wtype == 'listbox':
                    widget = self.createListbox(frame, **wconfig, grid={**wconfig.get('grid', {}), 'row': wrow})
                elif wtype == 'button':
                    widget = self.createButton(frame, **wconfig, grid={**wconfig.get('grid', {}), 'row': wrow})
                
                widgets[wname] = widget
                row = max(row, wrow + 1)
        
        # Add buttons
        if buttons:
            for btn_config in buttons:
                btn_text = btn_config['text']
                btn_command = btn_config['command']
                btn_column = btn_config.get('column', 0)
                btn_state = btn_config.get('state', 'normal')
                btn_kwargs = btn_config.get('kwargs', {})
                
                button = self.createButton(
                    frame,
                    btn_text,
                    btn_command,
                    grid={"column": btn_column, "row": row, "pady": 10, "sticky": "ew"},
                    state=btn_state,
                    **btn_kwargs
                )
                widgets[f'_button_{btn_text.lower().replace(" ", "_")}'] = button
        
        return {
            'window': window,
            'frame': frame,
            'widgets': widgets
        }


    def changeCourseBinAttribute(self, courseObj:CourseClass.Course, NEWattribute:str, OLDattribute:str, filepath ,newValue):
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

    def courseFilename(self, courseObj:CourseClass.Course):
        # filename with a uuid to avoid douplicates
        name = self.safeafyFileName(courseObj.nameAbreviated)
        rev = self.safeafyFileName(courseObj.revisionNumber)
        date = self.safeafyFileName(courseObj.date.replace("/", "-"))
        filename = f"{name}_{rev}_{date}.bin"
        return filename


    # When a new course, save to unique binary file
    def saveCourseToFile(self, courseObj:CourseClass.Course):
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
    # ============================================================================
    # Simplified Course Form (without assessment complexity)
    # ============================================================================

    def courseForm(self):
        """
        Example showing how to create a simple course form.
        Note: The actual newCourseForm has complex assessment logic that would
        need additional_widgets and custom callbacks.
        """
        
        def submit():
            # Get all field values
            courseName = self.courseNameEntry.get().strip() # type: ignore
            courseAbrev = self.courseAbbrevEntry.get().strip() # type: ignore
            courseTitle = self.courseTitleEntry.get().strip() # type: ignore
            revision = self.courseRevisionEntry.get().strip() # type: ignore
            dateOffered = self.courseDateEntry.get().strip() # type: ignore
            professor = self.professorNameEntry.get().strip() # type: ignore
            
            # Validation
            required_fields = [
                (courseName, "Course Name"),
                (courseAbrev, "Course Abbreviated Name"),
                (courseTitle, "Course Title"),
                (revision, "Revision Number"),
                (dateOffered, "Date Offered")
            ]
            
            for value, field_name in required_fields:
                if not value:
                    messagebox.showerror("Missing data", f"{field_name} is required.")
                    return
            
            # Create Course object (simplified - without assessments)
            import CourseClass as CourseClass
            courseObj = CourseClass.Course(
                name=courseName,
                nameAbreviated=courseAbrev,
                title=courseTitle,
                revisionNumber=revision,
                dateOffered=dateOffered,
                professorName=professor,
                students=[],
                assessments=[]
            )
            
            self.courses.append(courseObj)
            savedPath = self.saveCourseToFile(courseObj)
            messagebox.showinfo("Success", f"Course '{courseName}' submitted!\\nSaved to: {savedPath}")
            form_refs['window'].destroy() # type: ignore
        
        form_refs = self.addForm(
            title="New Course Form",
            geometry="500x400",
            form_title="New Course Form",
            fields=[
                {'label': 'Course Name:', 'name': 'courseName'},
                {'label': 'Course Abbreviated Name:', 'name': 'courseAbbrev'},
                {'label': 'Course Title:', 'name': 'courseTitle'},
                {'label': 'Revision Number:', 'name': 'courseRevision'},
                {'label': 'Date Offered:', 'name': 'courseDate'},
                {'label': 'Professor Name:', 'name': 'professorName'}
            ],
            buttons=[
                {'text': 'Submit Course', 'command': submit},
                {'text': 'Cancel', 'command': lambda: form_refs['window'].destroy(), 'column': 1} # type: ignore
            ]
        )

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

    # ============================================================================
    # Record Assessment Form with Listbox
    # ============================================================================

    def recordAssessmentForm_REFACTORED(self):
        """Refactored recordAssessmentForm using addForm with listbox"""
        
        def saveMark():
            selection = listbox.curselection()
            if not selection:
                messagebox.showwarning("No selection", "Select an assessment first.")
                return

            # Validate mark
            text = mark_entry.get().strip()
            try:
                mark = float(text)
            except ValueError:
                messagebox.showerror("Invalid mark", "Enter a number between 0 and 100.")
                return
            
            if mark < 0 or mark > 100:
                messagebox.showerror("Invalid mark", "Mark must be between 0 and 100.")
                return

            # Update assessment
            idx = selection[0]
            aid, weight, _old_mark = self.selectedStudent.assessments[idx]
            self.selectedStudent.assessments[idx] = (aid, weight, mark)
            
            self.saveSelectedCourse()
            finalGrade = self.calculateFinalGrade(self.selectedStudent)
            messagebox.showinfo("Saved", f"Saved mark for assessment {aid}.\\nFinal grade: {finalGrade}%")
            form_refs['window'].destroy() # type: ignore
        
        def onSelect(event=None):
            save_btn = form_refs['widgets']['_button_save_mark'] # type: ignore
            save_btn.config(state="normal" if listbox.curselection() else "disabled")
        
        # Preconditions
        def check_preconditions():
            if self.selectedCourse is None:
                return (False, "Select a course first.")
            if self.selectedStudent is None:
                return (False, "Select a student first.")
            return (True, "")
        
        # Create form
        form_refs = self.addForm(
            title="Record Assessment Mark",
            geometry="560x360",
            form_title=f"Student: {self.selectedStudent.name} ({self.selectedStudent.studentID})",
            fields=[
                {
                    'label': 'Select assessment:',
                    'name': 'assessments',
                    'widget_type': 'listbox',
                    'widget_options': {
                        'width': 70,
                        'height': 10,
                        'exportselection': False
                    }
                },
                {
                    'label': 'Enter mark (0-100):',
                    'name': 'mark'
                }
            ],
            buttons=[
                {'text': 'Save Mark', 'command': saveMark, 'column': 0, 'state': 'disabled'},
                {'text': 'Cancel', 'command': lambda: form_refs['window'].destroy(), 'column': 1} # type: ignore
            ],
            preconditions=check_preconditions
        )
        
        # Get widget references
        listbox = form_refs['widgets']['assessments'] # type: ignore
        mark_entry = form_refs['widgets']['mark'] # type: ignore
        
        # Populate listbox
        assessmentDictByID = {aid: aname for (aid, aname, _w) in self.selectedCourse.assessments}
        for (aid, weight, mark) in self.selectedStudent.assessments:
            aname = assessmentDictByID.get(aid, f"Assessment {aid}")
            listbox.insert(tk.END, f"ID {aid} | {aname} | Weight {weight}% | Mark {mark}%")
        
        # Bind selection event
        listbox.bind("<<ListboxSelect>>", onSelect)
        listbox.bind("<Double-Button-1>", onSelect)

    
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
            self.courseForm,
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
    # ============================================================================
    # Refactored addStudentForm
    # ============================================================================

    def addStudentForm(self):
        """Refactored using addForm method"""

        
        def submit():
            # Get form values from widgets
            name = self.studentNameEntry.get().strip()
            studentID = self.studentIDEntry.get().strip()
            start = self.startDateEntry.get().strip()
            tutor = self.tutorNameEntry.get().strip()

            if not name or not studentID or not start or not tutor:
                messagebox.showerror("Missing data", "Fill in all fields.")
                return
            
            # prevent duplicate student IDs
            for student in self.selectedCourse.registeredStudents:
                if student.studentID == studentID:
                    messagebox.showerror("Duplicate ID", f"Student ID {studentID} already exists.")
                    return
            
            # Create assessments for student
            studentAssessments = []
            for (assessmentID, assessmentName, weight) in self.selectedCourse.assessments:
                studentAssessments.append((assessmentID, weight, 0))
            
            # Create Student object
            import StundentClass as sdef
            student = sdef.Student(
                name=name,
                studentID=studentID,
                startDate=start,
                tutorName=tutor,
                assessments=studentAssessments
            )

            self.selectedCourse.registeredStudents.append(student)
            self.saveSelectedCourse()
            messagebox.showinfo("Success", f"Student '{name}' added.")
            form_refs['window'].destroy() # type: ignore
        
        # Precondition check
        def check_preconditions():
            if self.selectedCourse is None:
                return (False, "Please select a course first.")
            return (True, "")
        
        # Configure and create form
        form_refs = self.addForm(
            title="Add Student",
            geometry="400x300",
            form_title=f"Add A Student to: {self.selectedCourse.nameAbreviated if self.selectedCourse else 'N/A'}",
            fields=[
                {'label': 'Student Name:', 'name': 'studentName'},
                {'label': 'Student ID:', 'name': 'studentID'},
                {'label': 'Start Date (DD/MM/YYYY):', 'name': 'startDate'},
                {'label': 'Tutor Name:', 'name': 'tutorName'}
            ],
            buttons=[
                {'text': 'Add Student', 'command': submit, 'column': 0},
                {'text': 'Cancel', 'command': lambda: form_refs['window'].destroy(), 'column': 1} # type: ignore
            ],
            preconditions=check_preconditions
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
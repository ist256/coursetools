from .nbenvironment import NbEnvironment
from dateutil import tz
from datetime import datetime
from minio.error import S3Error
import time 

class Submission:

    def __init__(self, lesson = None, filename = None):
        try:
            self.env = NbEnvironment(lesson=lesson, filename=filename)
        except S3Error as e:
            print("ERROR: Likely cause: File is not in a course folder.")
            raise e
        except Exception as e:
            print(e)
            raise e

    @property
    def properties(self):
        return self.env.properties

    def submit_now(self,  ui=True, header_text="Submission Details", save_warning=True):
        if not self.env.is_assignment:
            raise Exception(f"ERROR: Thie file {self.env.filename} is not on the assignment list. Please check the assignment you are supposed to submit.")

        if not self.env.is_student:
            raise Exception(f"ERROR: Your netid {self.env.netid} does not appear on the {self.env.course} roster.")

        if ui:
            return self.__ui_submit(header_text = header_text, save_warning = save_warning, ignore_due_date=True)
        else:
            return self.__console_submit(header_text = header_text, save_warning = save_warning, ignore_due_date=True)

    def submit(self, ui=True, header_text="Submission Details", save_warning=True):
        if not self.env.is_assignment:
            raise Exception(f"ERROR: Thie file {self.env.filename} is not on the assignment list. Please check the assignment you are supposed to submit.")
            
        if not self.env.is_student:
            raise Exception(f"ERROR: Your netid {self.env.netid} does not appear on the {self.env.course} roster.")

        if ui:
            return self.__ui_submit(header_text=header_text, save_warning=save_warning)
        else:
            return self.__console_submit(header_text=header_text, save_warning=save_warning)

    def __ui_submit(self, header_text, save_warning, ignore_due_date=False):
        '''
        Perform a Submission from the UI
        '''        
        from ipywidgets import interact, interactive, fixed, interact_manual
        import ipywidgets as widgets
        from IPython.display import display, HTML, clear_output, Javascript

        def on_cancel_button_clicked(b):
            with out:
                clear_output()
                submit_button.disabled = True
                cancel_button.disabled = True
                display(HTML("Assignment submission cancelled. Re-run this cell to submit again."))

        def on_submit_button_clicked(b):
            with out:
                clear_output()
                submit_button.disabled = True
                cancel_button.disabled = True
                display(HTML("Submitting..."))
                if ignore_due_date:
                    result = self.env.mc.fput(self.env.bucket,self.env.filespec,self.env.assignment_target_file.replace("LATE-","") )
                else:
                    result = self.env.mc.fput(self.env.bucket,self.env.filespec,self.env.assignment_target_file)
                display(HTML(f"Your assignment was submitted! Reciept: <code>{result.etag}</code>"))

        submit_button = widgets.Button(
            description='Submit',
            disabled=False,
            button_style='success',
            tooltip='Submit',
            icon='check-circle'
        )
        cancel_button = widgets.Button(
            description='Cancel',
            disabled=False,
            button_style='danger',
            tooltip='Cancel',
            icon='times-circle'
        )

        submit_button.on_click(on_submit_button_clicked)
        cancel_button.on_click(on_cancel_button_clicked)
        target_file = self.env.mc.get_info(self.env.bucket, self.env.assignment_target_file)
        content = "<ul>"
        content += f"<li>Your NetID: <code>{self.env.netid}</code></li>"
        content += f"<li>Instructor NetID: <code>{self.env.instructor_netid}</code></li>"
        content += f"<li>Blackboard Gradebook Assignment Name: <code>{self.env.assignment['name']}</code></li>"
        content += f"<li>Total Points: <code>{self.env.assignment['total_points']}</code></li>"        
        content += f"<li>File You Are Submitting: <code>{self.env.filename}</code></li>"
        content += f"<li>Date/Time of Your Submission: <code>{self.env.run_datetime}</code></li>"
        if not ignore_due_date:
            content += f"<li>Due Date of the Assignment: <code>{self.env.assignment['duedate'] }</code></li>"
            if not self.env.assignment['on_time']: 
                content += f"<li><i class='fa fa-exclamation-circle' aria-hidden='true'></i> Your assignment is LATE!</li>"
                submit_button.description += " Late"

        if target_file is not None:
            last_mod = target_file.last_modified.astimezone(tz.gettz(self.env.timezone))
            content += (f"<li><i class='fa fa-exclamation-circle' aria-hidden='true'></i> Your assignment is a resubmission. You submitted on: <code>{self.env.to_datetime_string(last_mod)}</code>")
            submit_button.description = "Re-" + submit_button.description
        content += "</ul>"
        # Let's Save!!!
        display(Javascript("IPython.notebook.save_notebook()"),include=['application/javascript'])
        display(HTML(f"<h2>{header_text}</h2>"))
        display(HTML(content))
        if save_warning:
            display(HTML("<p style='color: #993333;'><i class='fa fa-save'></i> <b>To ensure your instructor has the most recent version, press <code>CTRL+S</code> to save your work before submitting.</b></p>"))

        display(widgets.HBox((submit_button,cancel_button)))
        out = widgets.Output()
        display(out)

    def __console_submit(self,header_text, save_warning):
        '''
        Perform a Submission from the command line
        '''
        WARN = "\U000026A0"
        CAL = "\U0001F553"
        POOP = "\U0001F4A9"
        OK = "\U00002705"
        BOMB = "\U0001F4A3"
        PYTHON = "\U0001F40D"
        RCPT = "\U0001F4C3"
        QUESTION = "\U00002753"
        CANCEL = "\U0000274C"
        UP = "\U00002B06"
        SAVE = "\U0001F4BE"
            
        if save_warning:
            print(f"-={SAVE}=- SAVE YOUR WORK. PRESS CTRL+S NOW -={SAVE}=-\n")
            time.sleep(5)

        print(f"\n-={PYTHON}=- {header_text.upper()} -={PYTHON}=-")
        print(f"Your Netid ............. {self.env.netid}")
        print(f"Your Instructor ........ {self.env.instructor_netid}")        
        print(f"Assigment File ......... {self.env.filename}")
        print(f"Submission Date ........ {self.env.run_datetime}")
        if not ignore_due_date:
            print(f"Assignment Due Date .... {self.env.assignment['duedate']}")

            if not self.env.assignment['on_time']:            
                print(f"\n{WARN}{WARN}{WARN} WARNING {WARN}{WARN}{WARN} Your Submission is LATE!")
                print(f"{CAL} Your Submission Date   : {self.env.run_datetime}")
                print(f"{CAL} Due Date For Assignment: {self.env.assignment['duedate']}")
                late_confirm = input(f"Submit This Assignment Anyways [y/n] {QUESTION}").lower()
                if late_confirm == 'n':
                    print(f"{CANCEL} Aborting Submission.")
                    return

        target_file = self.env.mc.get_info(self.env.bucket, self.env.assignment_target_file)
        if target_file != None:
                last_mod = target_file.last_modified.astimezone(tz.gettz(self.env.timezone))
                print(f"\n{WARN}{WARN}{WARN} WARNING {WARN}{WARN}{WARN} This is a Duplicate Submission!")
                print(f"{CAL} You Submitted This Assigment On: {self.env.to_datetime_string(last_mod)}")
                again = input(f"Overwrite Your Previous Submission [y/n] {QUESTION} ").lower()
                if again == 'n':
                    print(f"{CANCEL} Aborting Submission.")
                    return

        print(f"\n-={PYTHON}=- SUBMITTING -={PYTHON}=-")
        print(f"{UP} Uploading: {self.env.filename} ==> {self.env.assignment_target_file}")
        if ignore_due_date:
            result = self.env.mc.fput(self.env.bucket,self.env.filespec,self.env.assignment_target_file.replace("LATE-","") )
        else:
            result = self.env.mc.fput(self.env.bucket,self.env.filespec,self.env.assignment_target_file)
        print(f"{OK} Done!")
        print(f"{RCPT} Reciept: {result.etag}")


def submit_any():
    import pandas as pd
    from ipywidgets import interact, interactive, fixed, interact_manual
    import ipywidgets as widgets
    from datetime import datetime
    from dateutil import parser, tz
    from IPython.display import display, HTML, clear_output

    display(HTML(f"<h2>Select Assignment To Submit:</h2>"))

    submission = Submission()

    df = submission.env._NbEnvironment__assignments_df
    #display(df)

    duedate_col = df.columns[4]
    lesson_col = df.columns[0]
    assignment_col = df.columns[1]

    df['duedatedt'] = df.apply( lambda row: parser.parse(row[duedate_col]), axis=1)
    units = df[lesson_col].unique().tolist()

    unit_dropdown = widgets.Dropdown(
        options=units,
        value=units[0],
        description='Lesson:',
        layout={'width': 'max-content'},
        disabled=False
    )

    assignment_dropdown = widgets.Dropdown(
        options=df[df[lesson_col] == unit_dropdown.value].sort_values(assignment_col)[assignment_col].unique().tolist(),
        description='Assignment:',
        layout={'width': 'max-content'},
        disabled=False
    )

    assignment_date = widgets.Text(
        value=df[ df[assignment_col] == assignment_dropdown.value][duedate_col].values[0],
        description='Due Date:',
        disabled=True
    )

    assignment_status = widgets.Label(
        value="Unable to process this assignment. It is not past the due date!" if parser.parse(assignment_date.value)>= datetime.now() else "",
        description='Status:',
        disabled=True
    )

    button = widgets.Button(
        description="Select Assignment",
        icon="fa-check",
        button_style='primary',
        disabled = False)
    output = widgets.Output()

    #handlers
    def unit_dropdown_on_change(*args):
        assignment_dropdown.options = df[df[lesson_col] == unit_dropdown.value].sort_values(assignment_col)[assignment_col].unique().tolist()

    def assignment_dropdown_on_change(*args):
        assignment_date.value = df[ df[assignment_col] == assignment_dropdown.value][duedate_col].values[0]


    def on_button_clicked(b):
        with output:
            clear_output()
            newsub = Submission(lesson = unit_dropdown.value, filename = assignment_dropdown.value)
            header_text = f"Submission Details for {unit_dropdown.value} / {assignment_dropdown.value}"
            newsub.submit(ui=True, header_text = header_text, save_warning = False)


    #events
    unit_dropdown.observe(unit_dropdown_on_change)
    assignment_dropdown.observe(assignment_dropdown_on_change)
    button.on_click(on_button_clicked)

    #draw
    display(unit_dropdown, assignment_dropdown, assignment_date,button, assignment_status , output)
    assignment_dropdown_on_change()

import pandas as pd
import sys
import os
import math
from pyfiglet import Figlet
from PyInquirer import prompt
from tabulate import tabulate


# Validates numbers of command line argument.
def is_correct_num_args(args_num):
    return args_num == 2


# Validates is file exist
def is_file_exist(f_path):
    return os.path.isfile(f_path)


# Validates file data type.
def is_correct_file_type(ftype):
    return ftype.lower() == 'csv'


# Validates command line argument.
def is_correct_argu(cmd_args):
    args_num = len(cmd_args)
    if not is_correct_num_args(args_num):
        err_msg = 'Invalid argument: Require 1, got {0}.'.format(args_num - 1)
        raise ValueError(err_msg)

    f_path = cmd_args[1]
    if not is_file_exist(f_path):
        err_msg = "Invalid file path, {0} doesn't exist.".format(f_path)
        raise IOError(err_msg)

    f_type = f_path.split('.')[-1]
    if not is_correct_file_type(f_type):
        err_msg = 'Invalid file type: Require csv, got {0}.'.format(f_type)
        raise ValueError(err_msg)


# Read specified csv file.
def open_csv(f_path):
    try:
        return pd.read_csv(
                            f_path,
                            encoding='utf8',
                            dtype={
                                    'Subject': 'str', 'Year': 'str', 'Semester': 'str', 'Credit': 'int', 'Class': 'str',
                                    'Grade': 'str', 'Score': 'float'
                            }
                          )
    except Exception:
        raise


# Validates data input.
def validates(name, data):
    if name == 'Subject':
        return len(data) >= 12
    elif name == 'Year':
        return len(data) == 4 and data.isdigit()
    elif name == 'Semester':
        return len(data) == 1 and data.isdigit()
    elif name == 'Credit':
        return len(data) == 1 and data.isdigit()
    elif name == 'Section':
        return 1 <= len(data) <= 3 and data.isdigit()


# Insert grade of new subject.
def insert():
    global df
    questions = [
                    {
                        'type': 'input',
                        'name': 'Subject',
                        'message': 'Subject: ',
                        'validate': lambda subject: validates('Subject', subject)
                    },
                    {
                        'type': 'input',
                        'name': 'Year',
                        'message': 'Year: ',
                        'validate': lambda year: validates('Year', year)
                    },
                    {
                        'type': 'input',
                        'name': 'Semester',
                        'message': 'Semester: ',
                        'validate': lambda semester: validates('Semester', semester)
                    },
                    {
                        'type': 'input',
                        'name': 'Credit',
                        'message': 'Credit: ',
                        'validate': lambda credit: validates('Credit', credit)
                    },
                    {
                        'type': 'input',
                        'name': 'Section',
                        'message': 'Section: ',
                        'validate': lambda section: validates('Section', section)
                    },
                    {
                        'type': 'list',
                        'name': 'Grade',
                        'message': 'Grade:',
                        'choices': [
                            'A',
                            'B+',
                            'B',
                            'C+',
                            'C',
                            'D+',
                            'D',
                            'F'
                        ]
                    }
                ]
    try:
        answers = prompt(questions)
        df = df.append(answers, ignore_index=True)
    except Exception:
        raise


# Select subject to edit.
def select_subject():
    try:
        subject_choice = pd.Series(df.loc[:, 'Subject'])
        question = [
            {
                'type': 'list',
                'name': 'Subject',
                'message': 'Select subject? ',
                'choices': [subject for subject in subject_choice]
            }
        ]
        answer = prompt(question)
        return answer
    except Exception:
        raise


# Select content to edit.
def select_content(subject):
    try:
        contents = df.loc[df['Subject'] == subject['Subject']].loc[:, :'Grade'].to_dict()
        question = [
            {
                'type': 'list',
                'name': 'Content',
                'message': 'Select to edit? ',
                'choices': ['{0}({1})'.format(key, list(value.values())[0]) for key, value in contents.items()]
            }
        ]
        answer = prompt(question)
        return answer['Content'].split('(')[0]
    except Exception:
        raise


# Edit content.
def edit_content(content):
    try:
        if content != 'Grade':
            question = [
                    {
                        'type': 'input',
                        'name': 'Answer',
                        'message': '{0}: '.format(content),
                        'validate': lambda data: validates(content, data)
                    }
            ]
        else:
            question = [
                    {
                        'type': 'list',
                        'name': 'Answer',
                        'message': '{0}: '.format(content),
                        'choices': [
                            'A',
                            'B+',
                            'B',
                            'C+',
                            'C',
                            'D+',
                            'D',
                            'F'
                        ]
                    }
            ]
        answer = prompt(question)
        return answer
    except Exception:
        raise


# Edit subject information.
def edit():
    global df
    subject = select_subject()
    content = select_content(subject)
    answer = edit_content(content)
    try:
        df.loc[df['Subject'] == subject['Subject'], content] = answer['Answer']
    except Exception:
        raise


# Get semester list.
def get_semester():
    try:
        return pd.Series(df[['Year', 'Semester']].fillna('').values.tolist()).str.join(' ').drop_duplicates()
    except Exception:
        raise


# Select semester.
def select_semester(semester_list):
    try:
        question = [
                        {
                            'type': 'list',
                            'name': 'Semester',
                            'message': 'Select semester?',
                            'choices': [semester for semester in semester_list]
                        }
        ]
        answer = prompt(question)
        return answer['Semester']
    except Exception:
        raise


# Filter selected semester.
def filter_semester(year, semester):
    try:
        threshold = year + semester
        past_to_selected_semester = df.loc[:, :'Grade']
        past_to_selected_semester['Threshold'] = df['Year'] + df['Semester']
        past_to_selected_semester = past_to_selected_semester[(past_to_selected_semester['Threshold'].astype(int) <= int(threshold))].loc[:, :'Grade']
        selected_semester = past_to_selected_semester[(df['Year'] == year) & (df['Semester'] == semester)].loc[:, :'Grade']
        return selected_semester, past_to_selected_semester
    except Exception:
        raise


# Lookup grade score from grade
def lookup_grade_score(grade):
    grade_score = {'A': 4,
                   'B+': 3.5,
                   'B': 3,
                   'C+': 2.5,
                   'C': 2,
                   'D+': 1.5,
                   'D': 1
                   }
    return grade_score[grade]


# Create gpa report data frame.
def calculate_gpa(calculated_df, past_to_selected_semester):
    try:
        total_credit = calculated_df['Credit'].sum()
        total_score = (calculated_df['Score'] * calculated_df['Credit']).sum()
        gpa = math.floor(total_score / total_credit * 100) / 100

        collected_credit = past_to_selected_semester['Credit'].sum()
        collected_score = (past_to_selected_semester['Score'] * past_to_selected_semester['Credit']).sum()
        gpa_x = math.floor(collected_score / collected_credit * 100) / 100

        return {'total_credit': total_credit,
                'total_score': total_score,
                'gpa': gpa,
                'collected_credit': collected_credit,
                'collected_score': collected_score,
                'gpa_x': gpa_x
                }
    except Exception:
        raise


# Calculate grade report
def calculate_grade(selected_semester):
    try:
        year, semester = selected_semester.split(' ')
        calculated_df, past_to_selected_semester = filter_semester(year, semester)
        calculated_df['Score'] = df.apply(lambda row: lookup_grade_score(row['Grade']), axis=1)
        past_to_selected_semester['Score'] = df.apply(lambda row: lookup_grade_score(row['Grade']), axis=1)

        gpa_report_dict = calculate_gpa(calculated_df, past_to_selected_semester)
        return calculated_df, gpa_report_dict
    except Exception:
        raise


# Show grade and gpa of selected semester.
def view():
    semester_list = get_semester()
    selected_semester = select_semester(semester_list)
    calculated_df, gpa_report_dict = calculate_grade(selected_semester)
    print(tabulate(calculated_df, headers='keys', tablefmt='psql'))

    print('Total Credit: {0}'.format(gpa_report_dict['total_credit']))
    print('Total Score: {0}'.format(gpa_report_dict['total_score']))
    print('GPA: {0}'.format(gpa_report_dict['gpa']))
    print('Collected Credit: {0}'.format(gpa_report_dict['collected_credit']))
    print('Collected Score: {0}'.format(gpa_report_dict['collected_score']))
    print('GPAX: {0}'.format(gpa_report_dict['gpa_x']))


# Save and close program.
def save():
    df.to_csv(sys.argv[1], encoding='utf-8', index=False)
    print("Saved")
    print(Figlet(font='slant').renderText('Thank you'))
    exit()


# Show home page.
def show_home_page():
    answer = None
    question = [
            {
                'type': 'list',
                'name': 'main_menu',
                'message': 'Select option?',
                'choices': [
                    'Insert',
                    'Edit',
                    'View',
                    'Save & Close'
                ]
            }
    ]
    try:
        # Prompt homepage until select 'Save & Close'.
        while answer != 'Save & Close':
            print(Figlet(font='slant').renderText('Grading Report'))
            answer = prompt(question)

            if answer['main_menu'] == 'Insert':
                insert()
            elif answer['main_menu'] == 'Edit':
                edit()
            elif answer['main_menu'] == 'View':
                view()
            elif answer['main_menu'] == 'Save & Close':
                save()

    except Exception:
        raise


if __name__ == "__main__":
    is_correct_argu(sys.argv)
    df = open_csv(sys.argv[1])
    show_home_page()


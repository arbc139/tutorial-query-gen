#-*- coding: utf-8 -*-

import codecs
import datetime
import random
import math
import sys

from csv_manager import CsvReader
from utils import HangulPrinter, ValueGenerator, IdYearCalculator, RandomHelper, InsertSqlMaker, StringConverter

def parse_commands(argv):
  from optparse import OptionParser
  parser = OptionParser('"')
  parser.add_option('', '--facultyCount', dest='faculty_count')
  parser.add_option('', '--studentCount', dest='student_count')
  parser.add_option('', '--courseCount', dest='course_count')
  parser.add_option('', '--outputFile', dest='output_file')

  options, otherjunk = parser.parse_args(argv)
  return options

def main():
  options = parse_commands(sys.argv[1:])
  h_printer = HangulPrinter()

  # Static Tables
  # Read building.csv
  buildings = None
  with open('input/building.csv', 'r') as file:
    reader = CsvReader(file)
    buildings = reader.get_dict_list_data()
  # h_printer.pprint(buildings)

  # Read college.csv
  colleges = None
  with open('input/college.csv', 'r') as file:
    reader = CsvReader(file)
    colleges = reader.get_dict_list_data()
  # h_printer.pprint(colleges)

  # Read day_of_week.csv
  day_of_weeks = None
  with open('input/day_of_week.csv', 'r') as file:
    reader = CsvReader(file)
    day_of_weeks = reader.get_dict_list_data()
  # h_printer.pprint(day_of_weeks)

  # Read lectureroom.csv
  lecturerooms = None
  with open('input/lectureroom.csv', 'r') as file:
    reader = CsvReader(file)
    lecturerooms = reader.get_dict_list_data()
  # h_printer.pprint(lecturerooms)

  # Read semester.csv
  semesters = None
  with open('input/semester.csv', 'r') as file:
    reader = CsvReader(file)
    semesters = reader.get_dict_list_data()
  # h_printer.pprint(semesters)

  # Read timetable.csv
  timetables = None
  with open('input/timetable.csv', 'r') as file:
    reader = CsvReader(file)
    timetables = reader.get_dict_list_data()
  # h_printer.pprint(timetables)

  v_generator = ValueGenerator([x['MAJOR_ID'] for x in colleges])
  id_year_calculator = IdYearCalculator()
  r_helper = RandomHelper()

  faculty_count = len(colleges)
  student_count = 0
  course_count = 0
  if options.faculty_count is not None:
    faculty_count = int(options.faculty_count)
  if options.student_count is not None:
    student_count = int(options.student_count)
  if options.course_count is not None:
    course_count = int(options.course_count)

  # Dynamic Tables
  # Generate 'Faculty' table data
  faculties = []
  ids = v_generator.extract_ids(faculty_count)
  positions = ['정교수', '부교수', '조교수']
  # Must 1 Faculty on each College
  for college in colleges:
    faculty_id = ids.pop()
    faculties.append({
      'id': faculty_id,
      'name': v_generator.random_string(6),
      'major_id': college['MAJOR_ID'],
      'position': random.choice(positions),
    })
  for faculty_id in ids:
    college = random.choice(colleges)
    faculties.append({
      'id': faculty_id,
      'name': v_generator.random_string(6),
      'major_id': college['MAJOR_ID'],
      'position': random.choice(positions),
    })
  # h_printer.pprint(faculties)
  major_faculties = v_generator.get_major_faculties(faculties)

  # Generate 'Students' table data
  students = []
  ids = v_generator.extract_ids(student_count)
  for student_id in ids:
    college = random.choice(colleges)
    students.append({
      'id': student_id,
      'name': v_generator.random_string(6),
      'major_id': college['MAJOR_ID'],
      'admission_year': id_year_calculator.get_admission_year(student_id),
      'graduate_year': id_year_calculator.get_graduate_year(student_id),
      'grade': id_year_calculator.get_grade(student_id),
    })
  # h_printer.pprint(students)

  # Generate 'Courses' table data
  # -----!!----- unique key -----!!-----
  # YEAR, SEMESTER, COURSE_ID_PREFIX, COURSE_ID_NO, DIVISION_NO
  courses = []
  course_unique_keys = v_generator.get_course_unique_keys(
    count=course_count,
    years=[2015, 2016, 2017, 2018, 2019],
    semesters=[1, 2],
    # All majors + 3 Generals
    course_id_prefixes=v_generator.major_codes | set('XYZ'),
    # course_id_prefixes=v_generator.major_codes | v_generator.get_sample_general_codes(3),
  )
  for i, unique_key in enumerate(course_unique_keys):
    faculty = None
    if unique_key['course_id_prefix'] in major_faculties:
      faculty = random.choice(major_faculties[unique_key['course_id_prefix']])
    else:
      faculty = random.choice(faculties)
    lectureroom = random.choice(lecturerooms)
    courses.append({
      'id': i,
      'year': unique_key['year'],
      'semester': unique_key['semester'],
      'course_id_prefix': unique_key['course_id_prefix'],
      'course_id_no': unique_key['course_id_no'],
      'division_no': unique_key['division_no'],
      'course_name': unique_key['name'],
      'prof_id': faculty['id'],
      'build_no': lectureroom['BUILDNO'],
      'room_no': lectureroom['ROOMNO'],
      'credit': unique_key['credit'],
      'max_enrollees': random.randint(20, 300),
    })
  # h_printer.pprint(courses)

  # Generate 'Course_to_time' table data
  course_to_times = []
  week_timetables = v_generator.combine_week_timetables(day_of_weeks, timetables)
  # Time per credit (3 time for 3 credit)
  for course in courses:
    time = course['credit']
    course_timetables = random.sample(week_timetables, k=time)
    for ctt in course_timetables:
      course_to_times.append({
        'course_id': course['id'],
        'day_of_week': ctt[0],
        'no': ctt[1],
      })
  # h_printer.pprint(course_to_times)

  # Generate 'Course_registration' table data
  course_registrations = v_generator.combine_student_course(students, courses)
  # h_printer.pprint(course_registration)

  # Generate 'Attendance' table data
  # 3 credit = 48 hours, 2 credit = 32 hours, 1 credit = 16 hours
  attendances = []
  course_id_map = v_generator.get_course_id_map(courses)
  absence_probability_distribute = r_helper.non_uniform_distribute(
    [0,   0.2, 0.4, 0.6, 0.8, 1],
    [0.8, 0.1, 0.05, 0.02, 0.02, 0.01],
  )
  for cr in course_registrations:
    total_course_time = course_id_map[cr['course_id']]['credit'] * 16
    absence_time = int(total_course_time * random.choice(absence_probability_distribute))
    attendances.append({
      'course_id': cr['course_id'],
      'student_id': cr['student_id'],
      'absence_time': absence_time,
    })

  # Generate 'Grade' table data
  grades = []
  grade_map = {
    'A+': 4.3, 'A0': 4.0, 'A-': 3.7,
    'B+': 3.3, 'B0': 3.0, 'B-': 2.7,
    'C+': 2.3, 'C0': 2.0, 'C-': 1.7,
    'D+': 1.3, 'D0': 1.0, 'D-': 0.7,
    'F': 0.0,
  }
  for attendance in attendances:
    total_course_time = course_id_map[cr['course_id']]['credit'] * 16
    absence_time = attendance['absence_time']
    f_pivot = int(math.ceil(total_course_time / 3))
    grade_ch = None
    if absence_time >= f_pivot:
      grade_ch = 'F'
    else:
      grade_ch = random.choice(grade_map.keys())
    grades.append({
      'course_id': attendance['course_id'],
      'student_id': attendance['student_id'],
      'grade': grade_map[grade_ch],
    })

  sql_maker = InsertSqlMaker()
  with open(options.output_file, 'w+') as sql_file:
    # Faculty Table
    for faculty in faculties:
      sql = sql_maker.make_dict(
        table_name='FACULTY',
        columns=['ID', 'NAME', 'MAJOR_ID', 'POSITION'],
        value_info=[
          { 'key': 'id', 'type': 'STRING' },
          { 'key': 'name', 'type': 'STRING' },
          { 'key': 'major_id', 'type': 'STRING' },
          { 'key': 'position', 'type': 'STRING' },
        ],
        value_dict=faculty)
      sql_file.write(sql)
      sql_file.write('\n')

    # Students Table
    for student in students:
      sql = None
      if student['graduate_year'] is None:
        sql = sql_maker.make_dict(
          table_name='STUDENTS',
          columns=[
            'STUDENT_ID', 'NAME', 'MAJOR_ID', 'GRADE', 'ADMISSION_YEAR',
          ],
          value_info=[
            { 'key': 'id', 'type': 'STRING' },
            { 'key': 'name', 'type': 'STRING' },
            { 'key': 'major_id', 'type': 'STRING' },
            { 'key': 'grade', 'type': 'NUMBER' },
            { 'key': 'admission_year', 'type': 'NUMBER' },
          ],
          value_dict=student)
      else:
        sql = sql_maker.make_dict(
          table_name='STUDENTS',
          columns=[
            'STUDENT_ID', 'NAME', 'MAJOR_ID', 'GRADE', 'ADMISSION_YEAR',
            'GRADUATE_YEAR',
          ],
          value_info=[
            { 'key': 'id', 'type': 'STRING' },
            { 'key': 'name', 'type': 'STRING' },
            { 'key': 'major_id', 'type': 'STRING' },
            { 'key': 'grade', 'type': 'NUMBER' },
            { 'key': 'admission_year', 'type': 'NUMBER' },
            { 'key': 'graduate_year', 'type': 'NUMBER' },
          ],
          value_dict=student)
      sql_file.write(sql)
      sql_file.write('\n')

    # Courses Table
    for course in courses:
      sql = sql_maker.make_dict(
        table_name='COURSES',
        columns=[
          'COURSE_ID', 'YEAR', 'SEMESTER', 'COURSE_ID_PREFIX', 'COURSE_ID_NO',
          'DIVISION_NO', 'COURSE_NAME', 'PROF_ID', 'BUILDNO', 'ROOMNO',
          'CREDIT', 'MAX_ENROLLEES',
        ],
        value_info=[
          { 'key': 'id', 'type': 'NUMBER' },
          { 'key': 'year', 'type': 'NUMBER' },
          { 'key': 'semester', 'type': 'NUMBER' },
          { 'key': 'course_id_prefix', 'type': 'STRING' },
          { 'key': 'course_id_no', 'type': 'STRING' },
          { 'key': 'division_no', 'type': 'STRING' },
          { 'key': 'course_name', 'type': 'STRING' },
          { 'key': 'prof_id', 'type': 'STRING' },
          { 'key': 'build_no', 'type': 'STRING' },
          { 'key': 'room_no', 'type': 'STRING' },
          { 'key': 'credit', 'type': 'NUMBER' },
          { 'key': 'max_enrollees', 'type': 'NUMBER' },
        ],
        value_dict=course)
      sql_file.write(sql)
      sql_file.write('\n')

    # Courses_to_time Table
    for ctt in course_to_times:
      sql = sql_maker.make_dict(
        table_name='COURSE_TO_TIME',
        columns=[
          'COURSE_ID', 'DAY_OF_WEEK', 'NO',
        ],
        value_info=[
          { 'key': 'course_id', 'type': 'NUMBER' },
          { 'key': 'day_of_week', 'type': 'STRING' },
          { 'key': 'no', 'type': 'NUMBER' },
        ],
        value_dict=ctt)
      sql_file.write(sql)
      sql_file.write('\n')

    # Course_registrations Table
    for cr in course_registrations:
      sql = sql_maker.make_dict(
        table_name='COURSE_REGISTRATION',
        columns=['COURSE_ID', 'STUDENT_ID'],
        value_info=[
          { 'key': 'course_id', 'type': 'NUMBER' },
          { 'key': 'student_id', 'type': 'STRING' },
        ],
        value_dict=cr)
      sql_file.write(sql)
      sql_file.write('\n')

    # Attendance Table
    for attendance in attendances:
      sql = sql_maker.make_dict(
        table_name='ATTENDANCE',
        columns=['COURSE_ID', 'STUDENT_ID', 'ABSENCE_TIME'],
        value_info=[
          { 'key': 'course_id', 'type': 'NUMBER' },
          { 'key': 'student_id', 'type': 'STRING' },
          { 'key': 'absence_time', 'type': 'NUMBER' },
        ],
        value_dict=attendance)
      sql_file.write(sql)
      sql_file.write('\n')

    # Grade Table
    for grade in grades:
      sql = sql_maker.make_dict(
        table_name='GRADE',
        columns=['COURSE_ID', 'STUDENT_ID', 'GRADE'],
        value_info=[
          { 'key': 'course_id', 'type': 'NUMBER' },
          { 'key': 'student_id', 'type': 'STRING' },
          { 'key': 'grade', 'type': 'NUMBER' },
        ],
        value_dict=grade)
      sql_file.write(sql)
      sql_file.write('\n')

if __name__ == '__main__':
  main()
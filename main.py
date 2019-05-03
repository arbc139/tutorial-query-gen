#-*- coding: utf-8 -*-

import datetime
import sys

from csv_manager import CsvReader
from utils import HangulPrinter, ValueGenerator

insert_sql = 'INSERT INTO {table_name}({columns}) VALUES ({values});'

def parse_commands(argv):
  from optparse import OptionParser
  parser = OptionParser('"')
  parser.add_option('', '--facultyCount', dest='faculty_count')
  parser.add_option('', '--studentsCount', dest='student_count')
  parser.add_option('', '--courseCount', dest='course_count')
  parser.add_option('', '--crRatio', dest='cr_ratio') # course_registration_ratio
  # Must make 'COURSE_TO_TIME' by 1:1 to 'COURSE'

  options, otherjunk = parser.parse_args(argv)
  return options

def main():
  options = parse_commands(sys.argv[1:])
  h_printer = HangulPrinter()
  v_generator = ValueGenerator()

  faculty_count = int(options.faculty_count)
  student_count = int(options.student_count)
  school_ids = v_generator.school_ids(faculty_count + student_count)

  # Read building.csv
  building = None
  with open('input/building.csv', 'r') as file:
    reader = CsvReader(file)
    building = reader.get_dict_list_data()
  h_printer.pprint(building)

  # Read college.csv
  college = None
  with open('input/college.csv', 'r') as file:
    reader = CsvReader(file)
    college = reader.get_dict_list_data()
  h_printer.pprint(college)

  # Read day_of_week.csv
  day_of_week = None
  with open('input/day_of_week.csv', 'r') as file:
    reader = CsvReader(file)
    day_of_week = reader.get_dict_list_data()
  h_printer.pprint(day_of_week)

  # Read lectureroom.csv
  lectureroom = None
  with open('input/lectureroom.csv', 'r') as file:
    reader = CsvReader(file)
    lectureroom = reader.get_dict_list_data()
  h_printer.pprint(lectureroom)

  # Read semester.csv
  semester = None
  with open('input/semester.csv', 'r') as file:
    reader = CsvReader(file)
    semester = reader.get_dict_list_data()
  h_printer.pprint(semester)

  # Read timetable.csv
  timetable = None
  with open('input/timetable.csv', 'r') as file:
    reader = CsvReader(file)
    timetable = reader.get_dict_list_data()
  h_printer.pprint(timetable)

  # Generate Faculty table data
  faculty = None
  

  # table_name = 'test_student'
  # name = generate_random_string(5)
  # number = 2018111111
  # startdate = datetime.date(1950, 3, 1)
  # repeat = int(options.count)

  # with open(options.output_file, 'w+') as file:
  #   for _ in range(repeat):
  #     sql = insert_sql.format(**{
  #       'table_name': table_name,
  #       'name': "'{}'".format(name),
  #       'number': number,
  #       'startdate': "'{}'".format(startdate.strftime("%Y-%m-%d"))
  #     })
  #     file.write(sql)
  #     name = generate_random_string(5)
  #     number = number + 1
  #     startdate = startdate + datetime.timedelta(days=1)

if __name__ == '__main__':
  main()
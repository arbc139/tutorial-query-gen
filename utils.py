
import pprint
import itertools
import random
import string

class StringConverter():
  def sm_stringfy(self, value):
    return "'{}'".format(value)

  def bg_stringfy(self, value):
    return '"{}"'.format(value)

class InsertSqlMaker():
  def __init__(self):
    self.str_converter = StringConverter()
    self.sql_form = 'INSERT INTO {table_name}({columns}) VALUES ({values});'

  def make(self, table_name, columns, values):
    return self.sql_form.format(**{
      'table_name': self.str_converter.bg_stringfy(table_name),
      'columns': ','.join(
        self.str_converter.bg_stringfy(str(column)) for column in columns),
      'values': ','.join(str(value) for value in values),
    })

  def make_dict(self, table_name, columns, value_info, value_dict):
    values = []
    for info in value_info:
      if info['type'] == 'STRING':
        values.append(self.str_converter.sm_stringfy(value_dict[info['key']]))
      elif info['type'] == 'NUMBER':
        values.append(value_dict[info['key']])
    return self.make(table_name, columns, values)

class RandomHelper():
  def non_uniform_distribute(self, values, distributes):
    results = []
    for i in range(len(values)):
      value = values[i]
      distribute = int(distributes[i] * 100)
      results.extend([value] * distribute)
    return results

class IdYearCalculator():
  def __init__(self):
    self.today_year = 2019

  def get_year(self, target_id):
    return target_id / 1000000

  def get_admission_year(self, target_id):
    year = self.get_year(target_id)
    return year

  # Fast-graduate assumption
  def get_grade(self, target_id):
    year = self.get_year(target_id)
    raw_grade = self.today_year - year + 1
    if raw_grade > 5:
      return 5
    return raw_grade

  def get_graduate_year(self, target_id):
    grade = self.get_grade(target_id)
    if grade < 5:
      return None
    year = self.get_year(target_id)

    return year + 5

class ValueGenerator():
  def __init__(self, major_codes):
    self.sample_ids = range(2015000000, 2020000000)
    self.major_codes = set(major_codes)
    total_codes = set([''.join(i) for i in itertools.product(string.uppercase, repeat=3)])
    self.general_codes = total_codes - self.major_codes

  def random_string(self, length):
    return ''.join(random.choice(string.lowercase) for x in range(length))

  def random_digits(self, length):
    return ''.join(random.choice(string.digits) for x in range(length))

  def extract_ids(self, count):
    ids = [
      self.sample_ids.pop(random.randrange(len(self.sample_ids))) for _ in xrange(count)
    ]
    return ids

  def get_sample_general_codes(self, count):
    return set(random.sample(self.general_codes, k=count))

  def get_random_courses(self, count, course_id_prefixes):
    tuple_set = set()
    for _ in range(count):
      tuple_set.add((random.choice(course_id_prefixes), self.random_digits(4)))
    results = []
    for entry in tuple_set:
      results.append({
        'course_id_prefix': entry[0],
        'course_id_no': entry[1],
        'credit': random.randint(1, 3),
        'name': self.random_string(8),
      })
    return results

  # Course types
  # 0: only 1 course (2019)
  # 1: 2 divisions on 2019
  # 2: 2 divisions on 2 semesters
  # 3: 4 divisions on 2018~2019
  # 4: 4 divisions on 2015~2019
  def add_course_to_results(self, results, years, semesters, ctype, course):
    if ctype == 0:
      results.append({
        'year': years[-1],
        'semester': semesters[-1],
        'course_id_prefix': course['course_id_prefix'],
        'course_id_no': course['course_id_no'],
        'division_no': 1,
        'credit': course['credit'],
        'name': course['name'],
      })
      return
    elif ctype == 1:
      for division in range(1, 3):
        results.append({
          'year': years[-1],
          'semester': semesters[-1],
          'course_id_prefix': course['course_id_prefix'],
          'course_id_no': course['course_id_no'],
          'division_no': division,
          'credit': course['credit'],
          'name': course['name'],
        })
      return
    elif ctype == 2:
      for semester in semesters:
        for division in range(1, 3):
          results.append({
            'year': years[-1],
            'semester': semester,
            'course_id_prefix': course['course_id_prefix'],
            'course_id_no': course['course_id_no'],
            'division_no': division,
            'credit': course['credit'],
            'name': course['name'],
          })
      return
    elif ctype == 3:
      for year in years[-2:]:
        for semester in semesters:
          for division in range(1, 5):
            results.append({
              'year': year,
              'semester': semester,
              'course_id_prefix': course['course_id_prefix'],
              'course_id_no': course['course_id_no'],
              'division_no': division,
              'credit': course['credit'],
              'name': course['name'],
            })
      return
    elif ctype == 4:
      for year in years:
        for semester in semesters:
          for division in range(1, 5):
            results.append({
              'year': year,
              'semester': semester,
              'course_id_prefix': course['course_id_prefix'],
              'course_id_no': course['course_id_no'],
              'division_no': division,
              'credit': course['credit'],
              'name': course['name'],
            })
      return

  def get_course_unique_keys(self, count, years, semesters, course_id_prefixes):
    random_courses = self.get_random_courses(count, list(course_id_prefixes))
    results = []
    weighted_ctypes = [0] * 3 + [1] * 3 + [2] * 2 + [3] * 1 + [4] * 1
    for course in random_courses:
      ctype = random.choice(weighted_ctypes) # Randomly choosed
      self.add_course_to_results(results, years, semesters, ctype, course)
    return results

  def get_major_faculties(self, faculties):
    major_faculties = {}
    for k, g in itertools.groupby(faculties, key=lambda entry: entry['major_id']):
      if k not in major_faculties:
        major_faculties[k] = []
      major_faculties[k].extend(list(g))
    return major_faculties

  def get_course_id_map(self, courses):
    course_id_map = {}
    for k, g in itertools.groupby(courses, key=lambda entry: entry['id']):
      group = list(g)[0]
      course_id_map[k] = group
    return course_id_map

  def combine_week_timetables(self, day_of_weeks, timetables):
    day_of_weeks_set = set([x['DAY_OF_WEEK'] for x in day_of_weeks])
    timetables_set = set([x['NO'] for x in timetables])

    return list(itertools.product(day_of_weeks_set, timetables_set))

  def combine_student_course(self, students, courses):
    student_set = set([x['id'] for x in students])
    course_set = set([x['id'] for x in courses])

    course_id_enrollee_counter_map = {}
    for k, g in itertools.groupby(courses, key=lambda entry: entry['id']):
      group = list(g)[0]
      course_id_enrollee_counter_map[k] = {
        'count': 0,
        'max_enrollees': int(group['max_enrollees'] * random.uniform(0.3, 1)),
      }

    total_sc_set = list(itertools.product(student_set, course_set))
    sc_count = int(0.4 * len(total_sc_set))
    sc_set = random.sample(total_sc_set, k=sc_count)

    results = []
    for student_id, course_id in sc_set:
      enrollee_counter = course_id_enrollee_counter_map[course_id]

      if (enrollee_counter['count'] >= enrollee_counter['max_enrollees']):
        continue
      course_id_enrollee_counter_map[course_id]['count'] = enrollee_counter['count'] + 1
      results.append({
        'student_id': student_id,
        'course_id': course_id,
      })
    return results

# http://egloos.zum.com/mcchae/v/11076302
class HangulPrinter(pprint.PrettyPrinter):
  def format(self, _object, context, maxlevels, level):
    if isinstance(_object, unicode):
      return "'%s'" % _object.encode('utf8'), True, False
    elif isinstance(_object, str):
      _object = unicode(_object,'utf8')
      return "'%s'" % _object.encode('utf8'), True, False
    return pprint.PrettyPrinter.format(self, _object, context, maxlevels, level)

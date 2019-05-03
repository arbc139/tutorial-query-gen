
import pprint
import random
import string

class ValueGenerator():
  def random_string(self, length):
    return ''.join(random.choice(string.lowercase) for x in range(length))

  def school_ids(self, count):

  # 2019xxxxxx
  def school_id(self):
    years = ['2015', '2016', '2017', '2018', '2019']
    school_id_form = '{year}{code}'
    return school_id_form.format(**{
      'year': random.choice(years),
      'code': 
    })

class HangulPrinter(pprint.PrettyPrinter):
	def format(self, _object, context, maxlevels, level):
		if isinstance(_object, unicode):
			return "'%s'" % _object.encode('utf8'), True, False
		elif isinstance(_object, str):
			_object = unicode(_object,'utf8')
			return "'%s'" % _object.encode('utf8'), True, False
		return pprint.PrettyPrinter.format(self, _object, context, maxlevels, level)


#-*- coding: utf-8 -*-

import csv

class CsvWriter():

  def __init__(self, csvfile, fieldnames, is_writer=True):
    self.writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

  def write_header(self):
    self.writer.writeheader()

  def write_row(self, row):
    self.writer.writerow(row)

class CsvReader():

  def __init__(self, csvfile):
    self.reader = csv.DictReader(csvfile)

  def get_dict_list_data(self):
    result = []
    for row in self.reader:
      result.append(row)
    return result
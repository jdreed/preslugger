#!/usr/bin/python

import csv
import json
import sys
import pprint
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth 
from collections import defaultdict

import cStringIO as StringIO


class FormDefinition(dict):
    def __init__(self, *args, **kwargs):
        super(FormDefinition, self).__init__(*args, **kwargs)
        try:
            fnames = [x['name'] for x in self.fields]
        except KeyError:
            raise ValueError('Form definition contains field entry without name')
        if len(set(fnames)) != len(fnames):
            raise ValueError('Form definition has duplicate field names')

    def __getattr__(self, att):
        return self[att]

    def get_field_by_name(self, name):
        rv = [x for x in self.fields if x.get('name', '') == name]
        try:
            return rv[0]
        except IndexError:
            raise ValueError('Field {} not found'.format(name))
    
    @classmethod
    def load(cls, filename):
        with open(filename, 'r') as infile:
            return cls(json.load(infile))

class Form(object):
    def __init__(self, form_definition, font=('Courier', 10), xoffset=0, yoffset=0, filename=None):
        self.offset = (xoffset, yoffset)
        self.output = StringIO.StringIO() if filename is None else filename
        self.font = font
        self.form_definition = form_definition
        self.canvas = canvas.Canvas(self.output,
                                    pagesize=form_definition.page_size,
                                    bottomup=0)
        self.canvas.setFont(*self.font)

    def coords(self, x, y):
        return (x + self.offset[0], y + self.offset[1])
        
    def center_char_in_slug(self, char):
        text_width = stringWidth(char, *self.font)
        slug_width = self.form_definition.slug_size[0]
        return (slug_width - text_width) / 2.0

    def _rslug(self, x, y):
        x,y = self.coords(x, y)
        self.canvas.roundRect(x, y, *self.form_definition.slug_size, fill=True)

    def slug(self, x, y):
        self._rslug(x, y)

    def text(self, txt, x, y):
        x,y = self.coords(x, y)
        self.canvas.drawString(x, y, txt)

    def set_field(self, field, value):
        f = self.form_definition.get_field_by_name(field)
        if f['_type'] == "numeric":
            self.set_numeric_field(f, value)
        else:
            self.set_text_field(f, value)

    def set_text_field(self, field, value):
        self.text(value, *field['start'])

    def set_numeric_field(self, field, value):
        if len(value) > field['length']:
            raise ValueError('Value too long for field "{0[name]}"'.format(field))
        value = value.rjust(field['length'])
        if not value.strip().isdigit():
            raise ValueError('Field "{0[name]}" must be numeric')
        for i,n in enumerate(value):
            if n == ' ':
                continue
            col = field['start_col'] + (field['col_width'] * i)
            self.text(n, col + self.center_char_in_slug(n), field['text_row'])
            self.slug(col, field['slug_row'] + (field['row_height'] * int(n)))

    def test_page(self):
        dct = {}
        for f in self.form_definition.fields:
            dct[f['name']] = f['name'].upper() if f['_type'] == 'text' else ''.join(map(str, range(f['length'])))
        self.page(dct)
        self.save()

    def page(self, field_defs):
        self.canvas.setFont(*self.font)
        for k,v in field_defs.items():
            self.set_field(k, v)
        self.canvas.showPage()

    def save(self):
        self.canvas.save()


formdef = FormDefinition.load('form_20170.json')

x = Form(formdef, filename='out.pdf')
x.test_page()
#x.page({'Name': 'Foo', 'Student ID Number': '123456789'})
x.save()


# #x = Form()
# data = {'speech' : defaultdict(list),
#         'interview' :defaultdict(list),
#         'objective' :defaultdict(list)}

# with open(sys.argv[1]) as csvfile:
#     reader = csv.reader(csvfile)
#     for row in reader:
#         if len(row) < 1:
#             continue
#         (id, team, fname, lname, speech_room, speech_time, interview_room,
#          interview_time, homeroom, seat) = row[0:10]
#         if homeroom == "'6208":
#             homeroom = '6208'
#         data['speech'][speech_room].append((id, fname, lname,
#                                             datetime.strptime(speech_time,
#                                                               '%H:%M:%S')))
#         # deliberate because interview room was worng in spread sheet
#         data['interview'][speech_room].append((id, fname, lname,
#                                                datetime.strptime(interview_time,
#                                                                  '%H:%M:%S')))
#         data['objective'][homeroom].append((id, fname, lname, seat))


# with open(sys.argv[1]) as csvfile:
#     reader = csv.reader(csvfile)
#     x = Form('4th_judges.pdf')
#     for row in reader:
#         if len(row) < 1:
#             continue
#         (id, team, fname, lname, speech_room, speech_time, interview_room,
#          interview_time, homeroom, seat) = row[0:10]
#         name = ' '.join([fname, lname])
#         name += ' ({0})'.format(id)
#         x.page(name, 'Speech (4th judge)', 'Room ' + speech_room,
#                datetime.strptime(speech_time,
#                                  '%H:%M:%S').strftime('%l:%M %p'),
#                '4    8', 
#                '      {0}'.format(id))
#         x.page(name, 'Interview (4th judge)', speech_room,
#                datetime.strptime(interview_time,
#                                  '%H:%M:%S').strftime('%l:%M %p'),
#                '4    9', 
#                '      {0}'.format(id))
#     x.save()

# for room in data['objective']:
#     x = Form('room{0}.pdf'.format(room))
#     for test_num, test_name in ((' 1', '1 - Lang & Lit'),
#                                 (' 2', '2 - Music'),
#                                 (' 3', '3 - Science'),
#                                 (' 4', '4 - Art'),
#                                 (' 5', '5 - Math'),
#                                 (' 6', '6 - Economics'),
#                                 ('11', '11 - Social Science')):
#         by_time = sorted(data['objective'][room], key=lambda x: int(x[3]), reverse=True)
#         for record in by_time:
#             name = ' '.join(record[1:3])
#             name += ' ({0})'.format(record[0])
#             x.page(name, test_name, 'Room {0}'.format(room),
#                    '3/15/2015',
#                    '    {0}'.format(test_num),
#                    '      {0}'.format(record[0]),
#                    'Seat {0}'.format(record[3]))
#     x.save()

# for room in data['interview']:
#     x = Form('room{0}.pdf'.format(room))
#     by_time = sorted(data['interview'][room], key=lambda x: x[3])
#     for record in by_time:
#         name = ' '.join(record[1:3])
#         name += ' ({0})'.format(record[0])
#         for j in range(1, 4):
#             x.page(name, 'Interview', 'Room {0}'.format(room),
#                    record[3].strftime('%l:%M %p'),
#                    '{0}    9'.format(j),
#                    '      {0}'.format(record[0]))
#     x.save()


# for room in data['speech']:
#     x = Form('room{0}.pdf'.format(room))
#     by_time = sorted(data['speech'][room], key=lambda x: x[3])
#     for record in by_time:
#         name = ' '.join(record[1:3])
#         name += ' ({0})'.format(record[0])
#         for j in range(1, 4):
#             x.name(name)
#             x.test('Speech')
#             x.teacher('Room {0}'.format(room))
#             x.date(record[3].strftime('%l:%M %p'))
#             x.test_id('{0}    8'.format(j))
#             x.student_id('      {0}'.format(record[0]))
#             x.page()
#     x.save()
#     reader = csv.reader(csvfile)
#     for row in reader:
#         print row
#         x.record(*row)
# x.save()


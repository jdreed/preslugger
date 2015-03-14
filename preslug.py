#!/usr/bin/python

import csv
import sys
from datetime import datetime
from reportlab.pdfgen import canvas

FORM_20170 = (419.76, 810.00)

class Form:
    ROW_HEIGHT = 12.02
    COL_WIDTH = 18
    ROW_0 = 165.27
    STUDENT_ID_COL_0 = 56.25
    TEST_ID_COL_0 = 254.25
    TXT_ROW_0 = 158
    TXT_OFFSET = 3

    FONT = 'Courier'
    FONT_SIZE = 10

    NAME = (87, 70)
    TEACHER = (87, 91)
    TEST = (87, 112)

    DATE = (287, 70)
    CLASS = (287, 91)
    PERIOD = (287, 112)


    def __init__(self, filename='out.pdf'):
        self.canvas = canvas.Canvas(filename,
                                    pagesize=FORM_20170,
                                    bottomup=0)
        self.canvas.setFont(self.FONT, self.FONT_SIZE)
        
    def _slug(self, x, y):
        self.canvas.rect(x, y, 11.25, 4.3, fill=True)

    def _rslug(self, x, y):
        self.canvas.roundRect(x, y, 11.5, 4.5, 2, fill=True)

    def slug(self, x, y):
        self._rslug(x, y)

    def text(self, txt, x, y):
        self.canvas.drawString(x, y, txt)

    def name(self, txt):
        self.text(txt, *self.NAME)

    def teacher(self, txt):
        self.text(txt, *self.TEACHER)
        
    def test(self, txt):
        self.text(txt, *self.TEST)

    def date(self, txt):
        self.text(txt, *self.DATE)

    def classn(self, txt):
        self.text(txt, *self.CLASS)

    def period(self, txt):
        self.text(txt, *self.PERIOD)

    def student_id(self, num_str):
        for i, n in enumerate(num_str):
            col = self.STUDENT_ID_COL_0 + (self.COL_WIDTH * i)
            self.text(n, col + self.TXT_OFFSET, self.TXT_ROW_0)
            self.slug(col, self.ROW_0 + (self.ROW_HEIGHT * int(n)))

    def test_id(self, num_str):
        for i, n in enumerate(num_str):
            col = self.TEST_ID_COL_0 + (self.COL_WIDTH * i)
            self.text(n, col + self.TXT_OFFSET, self.TXT_ROW_0)
            self.slug(col, self.ROW_0 + (self.ROW_HEIGHT * int(n)))

    def record(self, name, test, student_id, test_id, date=None):
        self.canvas.setFont(self.FONT, self.FONT_SIZE)
        self.name(name)
        self.test(test)
        self.date(datetime.now().strftime('%b %d %Y') if date is None else date)
        self.student_id(student_id.strip())
        self.test_id(test_id.strip())
        self.canvas.showPage()

    def save(self):
        self.canvas.save()

x = Form()
with open('test.csv') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        print row
        x.record(*row)
x.save()


# x = Form()
# x.name('Jonathan Reed')
# x.test('Social Science')
# x.date('today')
# x.student_id('1234567890')
# x.test_id('123456')
# x.save()


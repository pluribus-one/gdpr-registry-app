# Copyright (c) 2020 Igino Corona, Pluribus One SRL;
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU Affero General Public License as
#     published by the Free Software Foundation, either version 3 of the
#     License, or (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with this program.  If not, see https://www.gnu.org/licenses/

from io import BytesIO
from reportlab.platypus.doctemplate import Frame, PageBreak
from reportlab.platypus.tables import TableStyle
from reportlab.platypus import Paragraph, PageTemplate, Table as Tab, BaseDocTemplate
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.styles import ParagraphStyle as PS
from reportlab.lib.enums import TA_RIGHT, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.graphics import renderPDF
from svglib.svglib import svg2rlg
from collections import Counter
from django.template.defaultfilters import date as _date
from django.utils.translation import gettext as _
from datetime import datetime
from django.utils.timezone import localtime
from . import models
from registry import settings
import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def print_datetime(*args):
    return _date(localtime(*args), settings.DATETIME_DEFAULT_FORMAT)

def Table(data):
    styles = getSampleStyleSheet()
    styleN = styles["BodyText"]
    styleN.alignment = TA_LEFT
    styleN.fontSize = 8
    styleBH = styles["Normal"]
    styleBH.alignment = TA_RIGHT
    styleBH.fontSize = 8
    new_data = []
    for row in data:
        new_data.append([Paragraph(str(elm) if i==0 else "<em>%s</em>" % elm, style=styleN if i!=0 else styleBH) for i, elm in enumerate(row)])

    sty = TableStyle(
        [
            ('GRID', (1, 0), (1, len(data)), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]
    )
    return Tab(new_data, colWidths=[3*cm, 12*cm], style=sty)

def get_print_value(obj, field_name):
    value = getattr(obj, field_name)
    if isinstance(value, int):
        get_display = getattr(obj, 'get_%s_display' % field_name, None)
        if get_display:
            return get_display()
    elif value is None or value == '':
        return "-"
    elif isinstance(value, bool):
        return _("Yes") if value else _("No")
    elif isinstance(value, datetime):
        return print_datetime(value)
    return value

def get_data(obj, exclude_fields={}):
    cls = obj.__class__
    return [(field.verbose_name.capitalize(), get_print_value(obj, field.name))
            for field in cls._meta.get_fields()
            if field.name not in exclude_fields and
            getattr(obj, field.name, None) and
            getattr(field, 'verbose_name', None) and field.name != 'id']


def scale(drawing, scaling_factor):
    """
    Scale a reportlab.graphics.shapes.Drawing()
    object while maintaining the aspect ratio
    """
    scaling_x = scaling_factor
    scaling_y = scaling_factor

    drawing.width = drawing.minWidth() * scaling_x
    drawing.height = drawing.height * scaling_y
    drawing.scale(scaling_x, scaling_y)
    return drawing


class MyDocTemplate(BaseDocTemplate):

    def __init__(self, filename, org, margin=2*cm, sep=0.2*cm, **kw):
        self.allowSplitting = 0
        BaseDocTemplate.__init__(self, filename, **kw)
        self.margin = margin
        self.w, self.h = self.pagesize
        self.sep = sep
        self.org = org
        template = PageTemplate('normal', frames=[Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id='F1')], onPage=self.laterPages)
        self.addPageTemplates(template)
        self.PAGE_FOOTER_LEFT = _("GDPR Registry of Data Processing Activities for %s")
        self.PAGE_FOOTER_RIGHT = _("Page %d")
        self.GENERATED_ON = _("Report generated on {date}")
        self.POWERED_BY = _("Powered by")

    # Entries to the table of contents can be done either manually by
    # calling the addEntry method on the TableOfContents object or automatically
    # by sending a 'TOCEntry' notification in the afterFlowable method of
    # the DocTemplate you are using. The data to be passed to notify is a list
    # of three or four items countaining a level number, the entry text, the page
    # number and an optional destination key which the entry should point to.
    # This list will usually be created in a document template's method like
    # afterFlowable(), making notification calls using the notify() method
    # with appropriate data.

    def generated_on(self):
        return self.GENERATED_ON.format(date=print_datetime())

    def afterFlowable(self, flowable):
        "Registers TOC entries."
        if flowable.__class__.__name__ == 'Paragraph':
            text = flowable.getPlainText()
            style = flowable.style.name
            if style == 'Heading1':
                level = 0
            elif style == 'Heading2':
                level = 1
            elif style == 'Heading3':
                level = 2
            elif style == 'Heading4':
                level = 3
            elif style == 'Heading5':
                level = 4
            else:
                return
            E = [level, text.split('>')[-1].strip(), self.page]
            #if we have a bookmark name append that to our notify data
            bn = getattr(flowable,'_bookmarkName',None)
            if bn is not None: E.append(bn)
            self.notify('TOCEntry', tuple(E))

    def firstPage(self, canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica-Bold', 16)
        canvas.drawCentredString(self.w/2, self.h/2-(2*cm), self.title)
        drawing = self.get_pluribus_drawing()
        scale(drawing, scaling_factor=0.3)
        renderPDF.draw(drawing, canvas, self.w/2 - (drawing.width / 2), self.h/2)
        canvas.setFont('Helvetica', 8)
        canvas.drawString(self.margin, self.margin, "First Page / Pluribus One")
        canvas.restoreState()

    def laterPages(self, canvas, doc):
        canvas.saveState()
        canvas.setLineWidth(3)
        canvas.setFont('Helvetica', 8)
        drawing = self.get_pluribus_drawing()
        scale(drawing, scaling_factor=0.1)
        canvas.line(self.margin, self.margin-self.sep, self.w-self.margin, self.margin-self.sep)
        canvas.line(self.margin, self.h-self.margin+self.sep, self.w-self.margin, self.h-self.margin+self.sep)
        canvas.drawString(self.margin, self.h-self.margin+3*self.sep, self.generated_on())
        canvas.drawString(self.margin, self.margin-3 * self.sep, self.PAGE_FOOTER_LEFT % self.org.name)
        canvas.drawRightString(self.w-self.margin, self.margin-3*self.sep, self.PAGE_FOOTER_RIGHT % doc.page)
        canvas.drawString(self.w-self.margin-drawing.width-1.6*cm, self.h-self.margin+3*self.sep, self.POWERED_BY)
        renderPDF.draw(drawing, canvas, self.w-drawing.width-self.margin, self.h-self.margin+2*self.sep)
        canvas.restoreState()


    def get_pluribus_drawing(self):
        return svg2rlg(os.path.join(BASE_DIR, 'audit/static/img/pluribus-one.svg'))


class PDFReport:
    """Report document in PDF"""

    def __init__(self, org, margin=3*cm, sep=0.2*cm):
        self.title = _("GDPR Registry of Processing Activities")
        self.org = org
        self.margin = margin
        self.pdf = None
        self.elements = []
        self.pagesize = A4
        self.sep = sep
        self.section = Counter()
        self.style = {'centered': PS(name = 'centered',
                        fontSize = 16,
                        leading = 15,
                        alignment = 1,
                        spaceAfter = 20),
                      'Normal': PS(name='Normal',
                                     fontSize=8),
                      1 : PS(
                        name = 'Heading1',
                        fontSize = 12,
                        leading = 14,
                        spaceBefore=10,
                        spaceAfter=15),
                      2 : PS(name = 'Heading2',
                        fontSize = 11,
                        leading = 13,
                        spaceBefore=10,
                        spaceAfter=14,),
                      3 : PS(name = 'Heading3',
                        fontSize = 10,
                        leading = 12,
                        spaceBefore=10,
                        spaceAfter=13),
                      4 : PS(name = 'Heading4',
                        fontSize = 9,
                        leading = 11,
                        spaceBefore=10,
                        spaceAfter=12),
                      5 : PS(name = 'Heading5',
                        fontSize = 8,
                        leading = 10,
                        spaceBefore=10,
                        spaceAfter=11)
                      }

    def create(self):
        buffer = BytesIO()
        doc = MyDocTemplate(buffer, pagesize=self.pagesize,
                                rightMargin=self.margin,
                                leftMargin=self.margin,
                                topMargin=self.margin,
                                bottomMargin=self.margin,
                                title=self.title,
                                sep=self.sep,
                                org=self.org,)
        self.set_elements()
        doc.multiBuild(self.elements)
        self.pdf = buffer.getvalue()
        buffer.close()


    def doHeading(self, text, num):
        sty = self.style.get(num)
        self.section.update([num])
        section_str = ".".join(str(self.section.get(key)) for key in range(1,6) if key in self.section)
        # this function makes our headings
        from hashlib import sha1
        # create bookmarkname
        bn = sha1(text.encode('utf8') + sty.name.encode('utf8')).hexdigest()
        # modify paragraph text to include an anchor point with name bn
        h = Paragraph('<b>%s <a name="%s"/></b>' % (text, bn), sty)
        # store the bookmark name on the flowable so afterFlowable can see this
        h._bookmarkName = bn
        self.elements.append(h)

    def set_toc(self):
        # Create an instance of TableOfContents. Override the level styles (optional)
        # and add the object to the story
        toc = TableOfContents()
        toc.levelStyles = [
            PS(fontSize=12, name='TOCHeading1', leftIndent=0, firstLineIndent=-20,  spaceBefore=0, leading=10),
            PS(fontSize=11, name='TOCHeading2', leftIndent=10, firstLineIndent=-20, spaceBefore=0, leading=10),
            PS(fontSize=10, name='TOCHeading3', leftIndent=20, firstLineIndent=-20, spaceBefore=0, leading=10),
            PS(fontSize=9, name='TOCHeading4', leftIndent=30, firstLineIndent=-20, spaceBefore=0, leading=10),
            PS(fontSize=8, name='TOCHeading5', leftIndent=40, firstLineIndent=-20, spaceBefore=0, leading=10),
        ]
        self.elements.append(Paragraph(self.title, self.style['centered']))
        #self.elements.append(Paragraph(_("Organization: <b>%s</b>") % self.org.name, self.style[1]))
        self.elements.append(toc)
        self.elements.append(PageBreak())

    def set_org(self):
        self.doHeading(_("Organization: %s") % self.org.name, 1)
        table = Table(get_data(self.org, exclude_fields={'business', 'officer'}))
        self.elements.append(table)

    def set_dpo(self):
        self.doHeading(_("Data Protection Officer"), 1)
        if self.org.officer:
            data = get_data(self.org.officer, exclude_fields={'user'})
            data.extend(get_data(self.org.officer.user, exclude_fields={'password', 'username',
                                                                        'groups',
                                                                        'user_permissions',
                                                                        'id', 'is_staff',
                                                                        'is_active',
                                                                        'date_joined'}))
            self.elements.append(Table(data))
        else:
            self.elements.append(Paragraph(_("DPO has not been set."), self.style['Normal']))

    def set_business(self):
        self.doHeading(_("Business Processes (%d)") % self.org.business.count(), 1)
        if self.org.business:
            for process in self.org.business.all():
                self.doHeading(_("Process: %s (activities: %d)") % (process.name, process.activities.count()), 2)
                self.elements.append(Table(get_data(process, exclude_fields={'activities', 'name'})))
                for activity in process.activities.all():
                    self.doHeading(_("%s > %s (data audits: %d)") % (process.name, activity.name, activity.data_audit.count()), 3)
                    self.elements.append(Table(get_data(activity, exclude_fields={'name', 'data_audit'})))
                    for data in activity.data_audit.all():
                        self.doHeading(_("%s > %s > %s") % (process.name, activity.name, data.name), 4)
                        self.elements.append(Table(get_data(data, exclude_fields={'name', 'subject_category',
                                                                                  'management', 'breach_detection',
                                                                                  'breach_response', 'dpia'})))
                        self.doHeading(_("%s > %s > %s > Data Subject Categories") % (process.name, activity.name, data.name), 5)
                        for cat in data.subject_category.all():
                            self.elements.append(Table(get_data(cat, exclude_fields={})))
                        if not data.subject_category.count():
                            self.elements.append(Paragraph(_("<em>There are no data subject categories for the data (!)</em>"), self.style['Normal']))

                        self.doHeading(_("%s > %s > %s > Data Management Policy") % (process.name, activity.name, data.name), 5)
                        if data.management:
                            self.elements.append(Table(get_data(data.management, exclude_fields={'data_transfer', 'processor_contracts'})))
                            self.doHeading(_("%s > %s > %s > Data Transfers (to third parties)") % (process.name, activity.name, data.name), 5)
                            for contract in data.management.processor_contracts.all():
                                self.elements.append(Table(get_data(contract, exclude_fields={'processor', 'pdfdocument_ptr'})))
                                self.elements.append(Table(get_data(contract.processor, exclude_fields={})))
                            if not data.management.processor_contracts.count():
                                self.elements.append(Paragraph(_("<em>Sounds Good. No data transfers.</em>"), self.style['Normal']))
                        else:
                            self.elements.append(Paragraph(_("<em>No Management Policy for the data (!)</em>"), self.style['Normal']))

                        self.doHeading(_("%s > %s > %s > Data Breach Detection") % (process.name, activity.name, data.name), 5)
                        if data.breach_detection:
                            self.elements.append(Table(get_data(data.breach_detection, exclude_fields={})))
                        else:
                            self.elements.append(Paragraph(_("<em>No Data Breach Detection method found (!)</em>"), self.style['Normal']))

                        self.doHeading(_("%s > %s > %s > Data Breach Response") % (process.name, activity.name, data.name), 5)
                        if data.breach_response:
                            self.elements.append(Table(get_data(data.breach_response, exclude_fields={})))
                        else:
                            self.elements.append(
                                Paragraph(_("<em>No Data Breach Response plan found (!)</em>"), self.style['Normal']))

                        self.doHeading(_("%s > %s > %s > Data Protection Impact Assessment") % (process.name, activity.name, data.name), 5)
                        if data.dpia:
                            self.elements.append(Table(get_data(data.dpia, exclude_fields={'pdfdocument_ptr'})))
                        else:
                            self.elements.append(
                                Paragraph(_("<em>No Data Protection Impact Assessment found (!)</em>"), self.style['Normal']))

        else:
            self.elements.append(Paragraph(_("<em>None available.</em>"), self.style['Normal']))

    def set_data(self):
        for elm in models.DataCategory.objects.all():
            p = Paragraph(elm.name, self.style['Normal'])
            self.elements.append(p)

    def set_page_break(self):
        self.elements.append(PageBreak())

    def set_elements(self):
        self.set_toc()
        self.set_org()
        self.set_dpo()
        self.set_business()

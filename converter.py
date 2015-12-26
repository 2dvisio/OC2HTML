#!/usr/bin/env python
'''
Created on 14 May 2015
@author: "Carmelo Velardo"
'''

__author__ = 'carmelo'


from optparse import OptionParser
import pymysql.cursors
import sys
import StringIO
import csv
import re
import fnmatch
import csv
import json


def convertOCType(text):
    if text == 'radio': return 'radiobuttons'
    elif text == 'single-select': return 'select'
    elif text == 'multi-select': return 'checkboxes'
    elif text == 'checkbox': return 'checkboxes'
    else: return text


def combineOptions(opt, vals):
    VALS = vals.split(',')
    OPTS = opt.split(',')

    OptionsElement = {}

    for i in range(0, len(VALS)):
        #if OPTS[i].strip() != '' and VALS[i].strip() != '':
        OptionsElement[VALS[i].strip()] = OPTS[i].strip()

    return OptionsElement



if __name__ == '__main__':

    VERSION_BIG = 1
    VERSION_SMALL = 1


    usage = "usage: %prog [options] arg"
    parser = OptionParser(usage)

    parser.add_option("-i", "--input", dest="input", help="input CRF file")
    parser.add_option("-o", "--output", dest="output", help="output elaborated html")
    parser.add_option("-u", "--user_db", help="user of database. ")
    parser.add_option("-p", "--pass_db", help="password of database. ")
    parser.add_option("-n", "--name_db", help="the database name. ")
    parser.add_option("-s", "--versionsmall", help="small version number. minor changes")
    parser.add_option("-b", "--versionbig", help="big version number. major changes")


    (options, args) = parser.parse_args(sys.argv)


    connection = None

    if options.user_db and options.pass_db :
        connection = pymysql.connect(host='localhost', user=options.user_db, passwd=options.pass_db, port=8889, db=options.name_db, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)

    if options.versionsmall and options.versionbig :
        VERSION_BIG = options.versionbig
        VERSION_SMALL = options.versionsmall



    input = None
    output = None

    if options.input:
        input = open(options.input, 'rU')

    if options.output:
        output = open(options.output, 'w')

    if input is None:
        parser.error("You must provide at least a valid input files.")


    reader = csv.reader(input, delimiter=',')

    lineNumber=0

    '''
    This is the schema
    0	name	            ITEM_NAME
    1	label_short	        DESCRIPTION_LABEL
    2	caption	            LEFT_ITEM_TEXT
    3	units	            UNITS
    4		                RIGHT_ITEM_TEXT
    5	section	            SECTION_LABEL
    6	group	            GROUP_LABEL
    7		                HEADER
    8		                SUBHEADER
    9		                PARENT_ITEM
    10		                COLUMN_NUMBER
    11		                PAGE_NUMBER
    12		                QUESTION_NUMBER
    13	type	            RESPONSE_TYPE
    14	???	                RESPONSE_LABEL
    15	options	            RESPONSE_OPTIONS_TEXT
    16	options_values	    RESPONSE_VALUES_OR_CALCULATIONS
    17		                RESPONSE_LAYOUT
    18		                DEFAULT_VALUE
    19	data_type	        DATA_TYPE
    20		                WIDTH_DECIMAL
    21	validation_regex	VALIDATION
    22	validation_message	VALIDATION_ERROR_MESSAGE
    23		                PHI
    24	required	        REQUIRED
    25	display_status  	ITEM_DISPLAY_STATUS
    26	display_condition	SIMPLE_CONDITIONAL_DISPLAY
    '''

    def isOK(data):
        return data != None and data != ''


    clusterSection = ''
    clusterGroup = ''

    ALL_FORM_ELEMENTS = {}
    DICTIONARY_ELEMENTS = {}


    for row in reader:

        lineNumber+=1
        if len(row) < 1 or lineNumber == 1:
            continue
        if row[0] == "" or row[0] is None or row[13] == "" or row[13] is None:
            continue

        section = ''
        sectionFull = ''
        if isOK(row[5]):
            sectionFull = row[5]
        section = "".join(sectionFull.split())

        if section != '' and section is not None:
            if section not in ALL_FORM_ELEMENTS:
                ALL_FORM_ELEMENTS[section] = []
            if section not in DICTIONARY_ELEMENTS:
                DICTIONARY_ELEMENTS[section] = []


        if clusterSection != row[5]:
            SINGLE_ELEMENT = {}
            SINGLE_ELEMENT['type'] = 'p'
            SINGLE_ELEMENT['class'] = 'section'
            SINGLE_ELEMENT['html'] = row[5]
            ALL_FORM_ELEMENTS[section].append(SINGLE_ELEMENT)
            clusterSection = row[5]

        if clusterGroup != row[6]:
            SINGLE_ELEMENT = {}
            SINGLE_ELEMENT['type'] = 'p'
            SINGLE_ELEMENT['class'] = 'group'
            SINGLE_ELEMENT['html'] = row[6]
            ALL_FORM_ELEMENTS[section].append(SINGLE_ELEMENT)
            clusterGroup = row[6]


        SINGLE_ELEMENT = {}

        SINGLE_ELEMENT['name'] = row[0]
        SINGLE_ELEMENT['id'] = row[0]
        SINGLE_ELEMENT['type'] = convertOCType(row[13].strip())

        # In case of checkboxes transform the element
        # into an array otherwise we will receive only
        # the last selection at the server
        if SINGLE_ELEMENT['type'] == 'checkboxes':
            SINGLE_ELEMENT['name'] += '[]'


        validate = {}

        if isOK(row[24]) and (row[24] == '1' or row[24] == 1):
            SINGLE_ELEMENT['validate'] = {'required': True, 'min': 0}


        if isOK(row[2]):
            SINGLE_ELEMENT['caption'] = row[2]

        if isOK(row[15]) and isOK(row[16]):
            SINGLE_ELEMENT['options'] = combineOptions(row[15], row[16])

        # Activates the datepicker
        if isOK(row[19]) and row[19] == 'DATE':
            SINGLE_ELEMENT['datepicker'] = {}

        # Substitute the type with number
        if SINGLE_ELEMENT['type'] == 'text' and isOK(row[19]) and (row[19] == 'INT' or row[19] == 'REAL'):
            SINGLE_ELEMENT['type'] = 'number'

        if isOK(row[3]):
            SINGLE_ELEMENT['units'] = row[3]

        if isOK(row[5]):
            SINGLE_ELEMENT['section'] = row[5]

        if isOK(row[6]):
            SINGLE_ELEMENT['oc_group'] = row[6]

        ENCLOSING_ENVELOP = {}
        ENCLOSING_ENVELOP['type'] = 'div'
        ENCLOSING_ENVELOP['class'] = 'envelop'
        ENCLOSING_ENVELOP['html'] = SINGLE_ELEMENT

        ALL_FORM_ELEMENTS[section].append(ENCLOSING_ENVELOP)


        if SINGLE_ELEMENT['type'] != 'p' and SINGLE_ELEMENT['type'] != 'div':
            DICTIONARY_ELEMENTS[section].append(SINGLE_ELEMENT['name'])


           # '<link rel="stylesheet" type="text/css" href="css/formalize.css"/>' \
           # '<script src="js/jquery.formalize.min.js"></script>' \
    html = '<link rel="stylesheet" type="text/css" href="css/dformStyle.css"/>' \
           '<script src="js/jquery.min.js"></script>' \
           '<script src="js/jquery-ui.min.js"></script>' \
           '<script src="js/jquery.dform-1.1.0.min.js"></script>'\
           '<script src="js/jquery.validate.min.js"></script>'\
           '<script src="js/additional-methods.min.js"></script>'


    # FINAL_ENVELOP = {}
    # FINAL_ENVELOP['type'] = 'tabs'
    # FINAL_ENVELOP['entries'] = []
    #
    # for Section, Elements in ALL_FORM_ELEMENTS.iteritems():
    #     F={}
    #     F['type'] = 'submit'
    #     F['value'] = 'Submit'
    #     Elements.append(F)
    #
    #     ELEMENT_TAB = {}
    #     ELEMENT_TAB['caption'] = Section
    #     ELEMENT_TAB['html'] = Elements
    #
    #     FINAL_ENVELOP['entries'].append(ELEMENT_TAB)
    #
    #
    #
    # html += '<form id="myform"></form><script type="text/javascript">$(function() {$("#myform").dform({ "action": "http://localhost:8888/supporthf2/plotFormData.php", "method": "post", "html": '
    # html += json.dumps(FINAL_ENVELOP)
    # html += '});});</script>'


    for Section, Elements in ALL_FORM_ELEMENTS.iteritems():
        if connection:
            query = "INSERT INTO data_forms(name,versionbig,versionsmall,form_schema) VALUES ('{0}',{1},{2},'{3}')".format(Section, VERSION_BIG, VERSION_SMALL, json.dumps(Elements))
            cur = connection.cursor()
            cur.execute(query)
            connection.commit()

        html += '<form id="myform'+Section+'"></form><script type="text/javascript">$(function() {$("#myform'+Section+'").dform({ "action": "http://localhost:8888/supporthf2/plotFormData.php", "method": "post", "html": '
        F={}
        F['type'] = 'submit'
        F['value'] = 'Submit'
        Elements.append(F)
        html += json.dumps(Elements)
        html += '});});</script>'



    D = {}
    for Section, Elements in DICTIONARY_ELEMENTS.iteritems():
         for i in Elements:
            if i not in D:
                D[i] = []
                D[i] = Section
    print json.dumps(D)


    output.write(html)

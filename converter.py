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
from openpyxl import load_workbook

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


row = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'AA']

def get(sheet, c, r):
    return sheet[row[c] + str(r)]
def getVal(sheet, c, r):
    if get(sheet, c, r) != None:
        return get(sheet, c, r).value
    else :
        return None
def isOK(data):
    return data != None and data != ''



if __name__ == '__main__':

    VERSION_BIG = 1
    VERSION_SMALL = 1


    usage = "usage: %prog [options] arg"
    parser = OptionParser(usage)

    parser.add_option("-i", "--input", dest="input", help="input CRF XLSX file")
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

    # Load the Workbook
    workbook = load_workbook(options.input)
    sheet_groups = workbook['Groups']
    sheet_sections = workbook['Sections']
    sheet_items = workbook['Items']

    starting_ind = 2
    Dictionary_Groups = {}

    while isOK(getVal(sheet_groups, 0, starting_ind)) :
        Dictionary_Groups[getVal(sheet_groups, 0, starting_ind)] = getVal(sheet_groups, 2, starting_ind)
        print('Added ' + getVal(sheet_groups, 0, starting_ind) + ' ' + Dictionary_Groups[getVal(sheet_groups, 0, starting_ind)])
        starting_ind += 1


    '''
    This is the schema for the Items sheet
    A 0	name	            ITEM_NAME
    B 1	label_short	        DESCRIPTION_LABEL
    C 2	caption	            LEFT_ITEM_TEXT
    D 3	units	            UNITS
    E 4		                RIGHT_ITEM_TEXT
    F 5	section	            SECTION_LABEL
    G 6	group	            GROUP_LABEL
    H 7		                HEADER
    I 8		                SUBHEADER
    J 9		                PARENT_ITEM
    K 10		                COLUMN_NUMBER
    L 11		                PAGE_NUMBER
    M 12		                QUESTION_NUMBER
    N 13	type	            RESPONSE_TYPE
    O 14	???	                RESPONSE_LABEL
    P 15	options	            RESPONSE_OPTIONS_TEXT
    Q 16	options_values	    RESPONSE_VALUES_OR_CALCULATIONS
    R 17		                RESPONSE_LAYOUT
    S 18		                DEFAULT_VALUE
    T 19	data_type	        DATA_TYPE
    U 20		                WIDTH_DECIMAL
    V 21	validation_regex	VALIDATION
    W 22	validation_message	VALIDATION_ERROR_MESSAGE
    X 23		                PHI
    Y 24	required	        REQUIRED
    Z 25	display_status  	ITEM_DISPLAY_STATUS
    AA 26	display_condition	SIMPLE_CONDITIONAL_DISPLAY
    '''
    clusterSection = ''
    clusterGroup = ''

    ALL_FORM_ELEMENTS = {}
    DICTIONARY_ELEMENTS = {}

    lineNumber=0
    ind = 1

    SI = sheet_items

    while isOK(getVal(SI,0,ind)):

        ind += 1

        print('Elaborating row ' + str(ind))
        #    for row in reader:
        # lineNumber+=1
        # if len(row) < 1 or lineNumber == 1:
        #     continue
        # if row[0] == "" or row[0] is None or row[13] == "" or row[13] is None:
        #     continue

        if not isOK(getVal(SI,0,ind)) or not isOK(getVal(SI,13,ind)):
            continue

        section = ''
        sectionFull = ''

        if isOK(getVal(SI,5,ind)):
            sectionFull = getVal(SI,5,ind)
        section = "".join(sectionFull.split())

        if section != '' and section is not None:
            if section not in ALL_FORM_ELEMENTS:
                ALL_FORM_ELEMENTS[section] = []
            if section not in DICTIONARY_ELEMENTS:
                DICTIONARY_ELEMENTS[section] = []


        if clusterSection != getVal(SI,5,ind):
            SINGLE_ELEMENT = {}
            SINGLE_ELEMENT['type'] = 'p'
            SINGLE_ELEMENT['class'] = 'section'
            SINGLE_ELEMENT['html'] = getVal(SI,5,ind)
            ALL_FORM_ELEMENTS[section].append(SINGLE_ELEMENT)
            clusterSection = getVal(SI,5,ind)

        if clusterGroup != getVal(SI,6,ind):
            SINGLE_ELEMENT = {}
            SINGLE_ELEMENT['type'] = 'p'
            SINGLE_ELEMENT['class'] = 'group'
            SINGLE_ELEMENT['html'] = Dictionary_Groups[getVal(SI,6,ind)]
            ALL_FORM_ELEMENTS[section].append(SINGLE_ELEMENT)
            clusterGroup = getVal(SI,6,ind)


        SINGLE_ELEMENT = {}

        SINGLE_ELEMENT['name'] = getVal(SI,0,ind)
        SINGLE_ELEMENT['id'] = getVal(SI,0,ind)
        SINGLE_ELEMENT['type'] = convertOCType(getVal(SI,13,ind).strip())

        # In case of checkboxes transform the element
        # into an array otherwise we will receive only
        # the last selection at the server
        if SINGLE_ELEMENT['type'] == 'checkboxes':
            SINGLE_ELEMENT['name'] += '[]'


        validate = {}

        if isOK(getVal(SI,24,ind)) and (getVal(SI,24,ind) == '1' or getVal(SI,24,ind) == 1):
            SINGLE_ELEMENT['validate'] = {'required': True, 'min': 0}


        if isOK(getVal(SI,2,ind)):
            SINGLE_ELEMENT['caption'] = getVal(SI,2,ind)

        if isOK(getVal(SI,15,ind)) and isOK(getVal(SI,16,ind)):
            SINGLE_ELEMENT['options'] = combineOptions(getVal(SI,15,ind), getVal(SI,16,ind))

        # Activates the datepicker
        if isOK(getVal(SI,19,ind)) and getVal(SI,19,ind) == 'DATE':
            SINGLE_ELEMENT['datepicker'] = {}

        # Substitute the type with number
        if SINGLE_ELEMENT['type'] == 'text' and isOK(getVal(SI,19,ind)) and (getVal(SI,19,ind) == 'INT' or getVal(SI,19,ind) == 'REAL'):
            SINGLE_ELEMENT['type'] = 'number'

        if isOK(getVal(SI,3,ind)):
            SINGLE_ELEMENT['units'] = getVal(SI,3,ind)

        if isOK(getVal(SI,5,ind)):
            SINGLE_ELEMENT['section'] = getVal(SI,5,ind)

        if isOK(getVal(SI,6,ind)):
            SINGLE_ELEMENT['oc_group'] = getVal(SI,6,ind)

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

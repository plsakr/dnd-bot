# -*- coding: utf-8 -*-

from collections import OrderedDict
from PyPDF2 import PdfFileWriter, PdfFileReader
import simplejson as json

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdftypes import resolve1



def _getFields(obj, tree=None, retval=None, fileobj=None):
    """
    Extracts field data if this PDF contains interactive form fields.
    The *tree* and *retval* parameters are for recursive use.

    :param fileobj: A file object (usually a text file) to write
        a report to on all interactive form fields found.
    :return: A dictionary where each key is a field name, and each
        value is a :class:`Field<PyPDF2.generic.Field>` object. By
        default, the mapping name is used for keys.
    :rtype: dict, or ``None`` if form data could not be located.
    """
    fieldAttributes = {'/FT': 'Field Type', '/Parent': 'Parent', '/T': 'Field Name', '/TU': 'Alternate Field Name',
                       '/TM': 'Mapping Name', '/Ff': 'Field Flags', '/V': 'Value', '/DV': 'Default Value'}
    if retval is None:
        retval = OrderedDict()
        catalog = obj.trailer["/Root"]
        # get the AcroForm tree
        if "/AcroForm" in catalog:
            tree = catalog["/AcroForm"]
        else:
            return None
    if tree is None:
        return retval

    obj._checkKids(tree, retval, fileobj)
    for attr in fieldAttributes:
        if attr in tree:
            # Tree is a field
            obj._buildField(tree, retval, fileobj, fieldAttributes)
            break

    if "/Fields" in tree:
        fields = tree["/Fields"]
        for f in fields:
            field = f.getObject()
            obj._buildField(field, retval, fileobj, fieldAttributes)

    return retval


def get_form_fields(infile):
    """Creates a OrderedDict containing all pdf form data

    Arguments:
        infile string -- the file name to process

    Returns:
        OrderedDict -- The form data from the pdf
    """    
    infile = PdfFileReader(open(infile, 'rb'))
    fields = _getFields(infile)
    return OrderedDict((k, v.get('/V', '')) for k, v in fields.items())


def get_form_in_dict(file_name):
    fp = open(file_name, 'rb') 
    parser = PDFParser(fp)
    doc = PDFDocument(parser)
    parser.set_document(doc)

    values = resolve1(doc.catalog['AcroForm'])['Fields']
    out = {}
    keys = []
    for i in values:
        field = resolve1(i)
        name, value = field.get('T'), field.get('V')
        try:
            if type(name) == bytes:
                name = name.decode('UTF-8')
            if type(value) ==  bytes:
                value = value.decode('UTF-8')
        except:
            hi = None
        out[name] = value
        keys.append(name)
    # print(out)
    return out


# if __name__ == '__main__':

#     pdf_file_name = 'Sahlo.pdf'

#     f = open("keys.txt", 'w+')
#     out = get_form_fields(pdf_file_name)
#     for i in out.keys():
#         f.write(i + "\n")
#     # f.write(json.dumps(get_form_fields(pdf_file_name)).replace("\\", ""))
#     f.close()
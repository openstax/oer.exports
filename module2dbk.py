"""
Copyright (c) 2013 - 2017 Rice University

This software is subject to the provisions of the
GNU AFFERO GENERAL PUBLIC LICENSE Version 3.0 (AGPL).

"""

import sys
import os
try:
    import Image
except:
    from PIL import Image
from StringIO import StringIO
import subprocess
import time

import urllib
import urllib2

import demjson as json
import jinja2
from lxml import etree
import util

from saxon import Saxon
import memcache
import hashlib


sax = None
mc = None
parser = etree.XMLParser(recover=True)

SAXON_PATH = util.resource_filename('lib', 'saxon9he.jar')
MATH2SVG_PATH = util.resource_filename('xslt2', 'math2svg-in-docbook.xsl')

DOCBOOK_BOOK_XSL = util.makeXsl('moduledbk2book.xsl')

MATH_XPATH = etree.XPath('//mml:math', namespaces=util.NAMESPACES)
DOCBOOK_SVG_IMAGE_XPATH = etree.XPath('//db:imagedata[svg:svg]',
                                      namespaces=util.NAMESPACES)
DOCBOOK_SVG_XPATH = etree.XPath('svg:svg', namespaces=util.NAMESPACES)
DOCBOOK_IMAGE_XPATH = etree.XPath('//db:imagedata[@fileref]',
                                  namespaces=util.NAMESPACES)

DEFAULT_EXERCISES_HOST = 'exercises.openstax.org'
DEFAULT_MATHMLCLOUD_URL = 'http://mathmlcloud.cnx.org:1337/equation/'

# -----------------------------
# Transform Structure:
#
# Every transform takes in 3 arguments:
# - xml doc
# - dictionary of files (string name, string bytes)
# - optional dictionary of parameters (string, string)
#
# Every transform returns:
# - xml doc
# - dictionary of new files
# - A list of log messages
#


def extractLog(entries):
    """ Takes in an etree.xsl.error_log and returns a list of dicts (JSON) """
    log = []
    for entry in entries:
        # Entries are of the form:
        # {'level':'ERROR','id':'id1234','msg':'Descriptive message'}
        text = entry.message
        if text:
            print >> sys.stderr, text.encode('utf-8')
        # try:
        #     dict = json.loads(text)
        #     errors.append(dict)
        # except ValueError:
        log.append({
          u'level': u'CRITICAL',
          u'id': u'(none)',
          u'msg': unicode(text)})


def makeTransform(file):
    xsl = util.makeXsl(file)

    def t(xml, files, **params):
        xml = xsl(xml, **params)
        errors = extractLog(xsl.error_log)
        return xml, {}, errors

    t.xsl_file = file
    return t

# c2p-files/cnxmathmlc2p.xsl does some disable-output-escaping="yes"
# so its output needs to be re-parsed
def makeTransformReparseAfter(file):
    xsl = util.makeXsl(file)

    def t(xml, files, **params):
        xml = xsl(xml, **params)
        errors = extractLog(xsl.error_log)

        parser = etree.XMLParser()
        xml = etree.parse(StringIO(etree.tostring(xml)), parser)
        return xml, {}, errors

    t.xsl_file = file
    return t

# legacy/zope runs under python2.4 - all() appeared in 2.5
def all(iterable):
    for element in iterable:
        if not element:
            return False
    return True

def compare_trees(e1, e2):
    if e1.tag != e2.tag: raise ValueError("Tags do not match. Returned '" + e1.tag + "' Expected '" + e2.tag + "'")
    if e1.text != e2.text: raise ValueError("Text does not match. Returned '" + e1.text + "' Expected '" + e2.text + "'")
    if e1.tail != e2.tail: raise ValueError("Tails do not match. Returned '" + e1.tail + "' Expected '" + e2.tail + "'")
    if e1.attrib != e2.attrib: raise ValueError("Attribs do not match. Returned '" + e1.attrib + "' Expected '" + e2.attrib + "'")
    if len(e1) != len(e2): raise ValueError("Child Lengths do not match. Returned '" + len(e1) + "' Expected '" + len(e2) + "'")
    return all(compare_trees(c1, c2) for c1, c2 in zip(e1, e2))


def _replace_tex_math(node, mml_url, retry=0):
    """call mml-api service to replace TeX math in body of node with mathml"""

    math = node.attrib['data-math'] or node.text
    if math is None:
        return None

    mc = memcache.Client(['127.0.0.1:11211'], debug=0)

    math_key = hashlib.md5(math.encode('utf-8')).hexdigest()

    eq = json.decode(mc.get(math_key) or '{}')

    if not eq:
        data = urllib.urlencode({'math': math.encode('utf-8'),
                                 'mathType': 'TeX',
                                 'mml': 'true'})
        req = urllib2.Request(mml_url, data)
        try:
            resp = urllib2.urlopen(req)
        except urllib2.HTTPError:
            return None

        if str(resp.code)[0] in ('2', '3'):
            eq = json.decode(resp.read())
            try:
                mc.set(math_key, json.encode(eq))
            except json.JSONEncodeError:
                print >> sys.stderr, ('WARNING: ERROR STORING MATH: "%s"'
                                      % (math.encode('utf-8')))

    if 'components' in eq and len(eq['components']) > 0:
        for component in eq['components']:
            if component['format'] == 'mml':
                mml = etree.fromstring(component['source'])
        if node.tag.endswith('span'):
            mml.set('display', 'inline')
        elif node.tag.endswith('div'):
            mml.set('display', 'block')
        mml.tail = node.tail
        return mml
    else:
        print >> sys.stderr, ('LOG: WARNING: Retry TeX conversion: %s'
                              % (json.encode(eq, compactly=False)))
        retry += 1
        if retry < 2:
            return _replace_tex_math(node, mml_url, retry)

    return None


def exercise_callback_factory(match, url_template, token=None, mml_url=None):
    """Create a callback function to replace an exercise by fetching from
    a server."""

    def _replace_exercises(elem):
        item_code = elem.get('url')[len(match):]
        url = url_template % (item_code)
        mc = memcache.Client(['127.0.0.1:11211'], debug=0)

        exercise = json.decode(mc.get(item_code + (token or '')) or '{}')

        if not exercise:
            if token:
                headers = {'Authorization': 'Bearer %s' % (token)}
                req = urllib2.Request(url, headers=headers)
            else:
                req = urllib2.Request(url)
            try:
                resp = urllib2.urlopen(req)
            except urllib2.HTTPError:
                print >> sys.stderr, ('WARNING: ERROR RETRIEVING EXERCISE: %s' % url)
                return None
            if str(resp.code)[0] in ('2', '3'):
                # grab the json exercise, run it through Jinja2 template,
                # replace element w/ it
                exercise = json.decode(resp.read())
                try:
                    mc.set(item_code + (token or ''), json.encode(exercise))
                except json.JSONEncodeError:
                    print >> sys.stderr, ('WARNING: ERROR STORING EXERCISE: "%s"'
                                          % (item_code))


        if exercise['total_count'] == 0:
            print >> sys.stderr, ('WARNING: MISSING EXERCISE: %s' % url)
            XHTML = '{%s}' % util.NAMESPACES['xhtml']
            missing = etree.Element(XHTML + 'div',
                                    {'class': 'missing-exercise'},
                                    nsmap=util.NAMESPACES)
            missing.text = 'MISSING EXERCISE: tag:%s' % (item_code)
            nodes = [missing]
        else:
            html = EXERCISE_TEMPLATE.render(data=exercise)
            try:
                nodes = etree.fromstring('<div>%s</div>' % (html))
            except etree.XMLSyntaxError:  # Probably HTML - convert
                body = etree.HTML(html)[0]
                nodes = etree.fromstring(etree.tostring(body))

            if mml_url:
                for node in nodes.xpath('//*[@data-math]'):
                    mparent = node.getparent()
                    mathml = _replace_tex_math(node, mml_url)
                    if mathml is not None:
                        mparent.replace(node, mathml)
                    else:
                        mathtext = node.get('data-math') or node.text or ''
                        print >> sys.stderr, ('WARNING: BAD TEX CONVERSION: "%s" URL: %s'
                                              % (mathtext.encode('utf-8'), url))
                        XHTML = '{%s}' % util.NAMESPACES['xhtml']
                        failed = etree.Element(XHTML + 'div',
                                               {'class': 'missing-exercise'},
                                               nsmap=util.NAMESPACES)
                        failed.text = 'FAILED TEX CONVERSION'
                        mparent.insert(mparent.index(node), failed)

        parent = elem.getparent()
        if etree.QName(parent.tag).localname == 'para':
            elem = parent
            parent = elem.getparent()

        parent.remove(elem)  # Special case - assumes single wrapper elem
        parent.set('data-retrieved-from', item_code)
        for child in nodes:
            parent.append(child)

    xpath = '//c:link[contains(@url, "%s")]' % (match)
    return (xpath, _replace_exercises)


def benchmark_transform(i, transform, time_taken, benchmark):
    transform_name = transform.__name__
    if transform_name == 't':
        transform_name = transform.xsl_file
    transform_name = '%02d. %s' % (i + 1, transform_name)
    if transform_name in benchmark:
        benchmark[transform_name] += time_taken
    else:
        benchmark[transform_name] = time_taken


# Main method. Doing all steps for the Google Docs to CNXML transformation
def convert(moduleId, xml, filesDict, collParams, temp_dir, svg2png=True, math2svg=True, reduce_quality=False, benchmark=None):
    """ Convert a cnxml file (and dictionary of filename:bytes) to a Docbook file and dict of filename:bytes) """

    #if 'index.included.dbk' in filesDict:
    #  print >> sys.stderr, "LOG: Using already converted dbk file!"
    #  return (filesDict['index.included.dbk'], {})
    #print >> sys.stderr, "LOG: Working on Module %s" % moduleId
    # params are XPaths so strings need to be quoted
    params = {'cnx.module.id': "'%s'" % moduleId, 'cnx.svg.chunk': 'false'}
    params.update(collParams)

    def expand_exercises(xml, files, **params):
        """Finds magic hrefs, and expands them by fetching from exercises server"""
        exercise_host = DEFAULT_EXERCISES_HOST
        mml_url = DEFAULT_MATHMLCLOUD_URL
        exercise_token = None
        exercise_url = 'https://%s/api/exercises?q=tag:' % (exercise_host) + '%s'
        exercise_match = '#ost/api/ex/'
        xpath, replace_exercise = exercise_callback_factory(exercise_match,
                                                            exercise_url,
                                                            exercise_token,
                                                            mml_url)

        to_replace = etree.XPath(xpath, namespaces=util.NAMESPACES)
        for exercise in to_replace(xml):
            replace_exercise(exercise)

        return xml, {}, [] # xml, newFiles, log messages

    def mathml2svg(xml, files, **params):
        try:
            global parser
            global sax
            global mc
            if sax is None:
                sax = Saxon()

            if mc is None:
                mc = memcache.Client(['127.0.0.1:11211'], debug=0)

            if not math2svg:
                return xml, {}, []

            formularList = MATH_XPATH(xml)
            math_list = []
            svgs = {}

            unprocessed = {}

            for mathml in formularList:
                mathml_key = hashlib.md5(etree.tostring(mathml)).hexdigest()
                math_list.append((mathml, mathml_key))
                svg_str = mc.get(mathml_key)
                if svg_str:
                    svgs[mathml_key] = svg_str
                else:
                    unprocessed[mathml_key] = mathml

            if len(unprocessed) > 0:
                mathml_str_list = [etree.tostring(mathml) for mathml in unprocessed.values()]
                mathml_tree_str = "<root>" + ''.join(mathml_str_list) + "</root>"
                mathml_svg_tree_str = sax.convert(mathml_tree_str)
                mathml_svg_tree = etree.parse(StringIO(mathml_svg_tree_str), parser)
                root = mathml_svg_tree.getroot()
                mathml_svg_list = root.getchildren()
                for  mathml_key, expected_mathml in unprocessed.items():
                    svg = mathml_svg_list.pop(0)
                    returned_mathml = mathml_svg_list.pop(0)
                    if compare_trees(returned_mathml, expected_mathml):
                        svg_str = etree.tostring(svg)
                        mc.set(mathml_key, svg_str)
                        svgs[mathml_key] = svg_str
                    else:
                        raise ValueError("returned mathml not expected")

            # All worked, now update XML tree
            for mathml, math_key in math_list:
                svg = etree.parse(StringIO(svgs[math_key]), parser).getroot()
                mathml.addprevious(svg)

        except RuntimeError:
            formularList = MATH_XPATH(xml)
            strErr = ''
            if len(formularList) > 0:

                # Take XML from stdin and output to stdout
                # -s:$DOCBOOK1 -xsl:$MATH2SVG_PATH -o:$DOCBOOK2
                strCmd = ['java','-jar', SAXON_PATH, '-s:-', '-xsl:%s' % MATH2SVG_PATH]

                # run the program with subprocess and pipe the input and output to variables
                p = subprocess.Popen(strCmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, close_fds=True)
                # set STDIN and STDOUT and wait untill the program finishes
                stdOut, strErr = p.communicate(etree.tostring(xml))

                #xml = etree.fromstring(stdOut, recover=True) # @xml:id is set to '' so we need a lax parser
                parser = etree.XMLParser(recover=True)
                xml = etree.parse(StringIO(stdOut), parser)

                if strErr:
                    print >> sys.stderr, strErr.encode('utf-8')

        return xml, {}, [] # xml, newFiles, log messages

    def imageResize(xml, files, **params):
        # TODO: parse the XML and xpath/annotate it as we go.
        newFiles = {}
        for position, image in enumerate(DOCBOOK_IMAGE_XPATH(xml)):
            filename = image.get('fileref')
            mimeType = image.getparent().get('format', 'JPEG')
            # Exception thrown if image doesn't exist
            if filename in files:
                try:
                    bytes = files[filename]
                    img = Image.open(StringIO(bytes))

                    width = img.size[0]
                    height = img.size[1]
                    if reduce_quality: # Only resize when in DEBUG mode (so content entry sees the High Resolution PDFs)
                        print >> sys.stderr, 'LOG: DEBUG: Reducing quality of %s (%s)' % (filename, mimeType)
                        # Always resave
                        fname = "_autogen-png2jpeg-%04d.jpg" % (position + 1)

                        bytesFile = StringIO()
                        img.save(bytesFile, 'jpeg', optimize=True, quality=30)
                        # Since we probably changed the type of file to JPEG change the format in the image tag
                        # The image type is used in the epub manifest to map images to their mime-type
                        image.set('fileref', fname)
                        image.set('format', 'JPEG')
                        image.getparent().set('format', 'JPEG')

                        newFiles[fname] = bytesFile.getvalue()

                except IOError:
                    print >> sys.stderr, 'LOG: WARNING: Malformed image %s' % filename
            else:
                print >> sys.stderr, 'LOG: WARNING: Image missing %s' % filename
                pass
        return xml, newFiles, [] # xml, newFiles, log messages

    # Convert SVG elements to PNG files
    # (this mutates the document)
    def svg2pngTransform(xml, files, **params):
        newFiles2 = {}
        if svg2png:
            for position, image in enumerate(DOCBOOK_SVG_IMAGE_XPATH(xml)):
                print >> sys.stderr, 'LOG: Converting SVG to PNG'
                # TODO add the generated file to the edited files dictionary
                strImageName = "_autogen-svg2png-%04d.png" % (position + 1)
                svg = DOCBOOK_SVG_XPATH(image)[0]
                svgStr = etree.tostring(svg)

                pngStr = util.svg2png(svgStr)
                newFiles2[strImageName] = pngStr
                image.set('fileref', strImageName)
                image.set('format', 'PNG')
                image.getparent().set('format', 'PNG')

        return xml, newFiles2, [] # xml, newFiles, log messages

    PIPELINE = [
      makeTransformReparseAfter('cnxml-clean.xsl'),
      makeTransform('cnxml-clean-math.xsl'),
      # Have to run the cleanup twice because we remove empty mml:mo,
      # then remove mml:munder with only 1 child.
      # See m21903
      makeTransform('cnxml-clean-math.xsl'),
      expand_exercises,  # Fetch exercises and convert contained latex math
      makeTransform('cnxml-clean-math-simplify.xsl'),   # Convert "simple" MathML to cnxml
      makeTransform('cnxml2dbk.xsl'),   # Convert to docbook
      mathml2svg,
      makeTransform('dbk-clean.xsl'),
      imageResize, # Resizing is done before svg2png because svg2png uses a reduced color depth
      svg2pngTransform,
      makeTransform('dbk-svg2png.xsl'), # Clean up the image attributes
      # dbk2xhtml,
    ]

    newFiles = {}
    origAndNewFiles = {}
    origAndNewFiles.update(filesDict)

    for i, transform in enumerate(PIPELINE):
        beginning = time.time()
        xml, newFiles2, errors = transform(xml, origAndNewFiles, **params)
        newFiles.update(newFiles2)
        origAndNewFiles.update(newFiles2)
        time_taken = time.time() - beginning
        benchmark_transform(i, transform, time_taken, benchmark)

    origAndNewFiles.update(newFiles)

    # Write out all files to the temp dir so they don't stay in memory
    for (key, value) in origAndNewFiles.items():
        print >> sys.stderr, "Writing out " + os.path.join(temp_dir, key)
        f = open(os.path.join(temp_dir, key), 'w')
        f.write(value)
        f.close()
    newFiles = {}

    now = time.time()
    # Create a standalone db:book file for the module
    dbkStandalone = DOCBOOK_BOOK_XSL(xml)
    newFiles['index.standalone.dbk'] = etree.tostring(dbkStandalone)
    # uncomment this to write out individual docbook module files
    #with open(os.path.join(temp_dir,'%s.dbk' % moduleId), 'w') as f:
    #  f.write(newFiles['index.standalone.dbk'])
    if 'standalone db:book file' in benchmark:
        benchmark['standalone db:book file'] += time.time() - now
    else:
        benchmark['standalone db:book file'] = time.time() - now

    return etree.tostring(xml), newFiles


EXERCISE_TEMPLATE = jinja2.Template("""\
{% if data['items'].0.questions %}
    {% for question in data['items'].0.questions %}
        <div xmlns="http://www.w3.org/1999/xhtml">{{ question.stem_html }}</div>
        {% if 'multiple-choice' in question.formats %}
            {% if question.answers %}
            <div class="orderedlist" xmlns="http://www.w3.org/1999/xhtml">
              <ol class="orderedlist" type="a">
                {% for answer in question.answers %}
                  <li{% if 'correctness' in answer
                      %} data-correctness={{ answer.correctness }} {%
                  endif %} class="listitem"><p>{{ answer.content_html }}</p></li>
                {% endfor %}
              </ol>
            </div>
            {% endif %}
        {% endif %}
    {% endfor %}
{% endif %}
""",  trim_blocks=True)

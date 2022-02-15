import copy
import glob
import os
import subprocess
from lxml import etree
from tqdm import tqdm

inputMappingFile = './mapping/mappings-zbz.x3ml'
generatorFile = './mapping/generator-policy.xml'

inputDir = './input/'
mappingDir = './mapping/'
outputDir = './output/'

mappingTempDir = os.path.join(mappingDir, "temp")
outputTempDir = os.path.join(outputDir, "temp")

MAPPING_ID_ZEROES = 4

def createOrEmptyDirectory(dir):
    if not dir:
        return False
    try:
        os.mkdir(dir)
    except:
        files = glob.glob(dir + "/*.*") 
        for f in files:
            try:
                os.remove(f)
            except OSError as e:
                print("Error: %s : %s" % (f, e.strerror))

def generateOutputGraph(*, inputDir, outputDir, mappings):
    from string import Template
    from rdflib.namespace import RDF
    from rdflib import Namespace, Literal, URIRef
    from rdflib.graph import Graph, ConjunctiveGraph
    from rdflib.plugins.stores.memory import Memory
    graphUriTemplate = Template("https://resource.swissartresearch.net/graph/record/${recordID}/mapping/${mappingId}")
    inputFiles = [d for d in os.listdir(inputDir) if os.path.isfile(os.path.join(inputDir, d)) and d.endswith(".ttl")]
    
    store = Memory()
    dataset = ConjunctiveGraph(store=store)

    for file in inputFiles:
        mappingID = int(file[-(4 + MAPPING_ID_ZEROES):][:-4])
        recordID = file.rsplit('/', 1)[-1][:-(5 + MAPPING_ID_ZEROES)]

        g = Graph()
        g.parse(os.path.join(inputDir, file))

        graphURI = URIRef(graphUriTemplate.substitute(recordID=recordID, mappingId=mappingID))
        graphCreationURI = URIRef(graphUriTemplate.substitute(recordID=recordID, mappingId=mappingID) + "/creation")
        d = Graph(store=store, identifier=graphURI)
        for triple in g:
            d.add(triple)

        d.add((graphURI, RDF.type, URIRef("http://www.cidoc-crm.org/cidoc-crm/E73_Information_Object")))
        d.add((graphURI, URIRef("http://www.cidoc-crm.org/cidoc-crm/P94i_was_created_by"), graphCreationURI))
        d.add((graphCreationURI, URIRef("http://www.cidoc-crm.org/cidoc-crm/P3_has_note"), Literal(etree.tostring(mappings[mappingID].find("mappings/mapping"), pretty_print=True))))
    
    dataset.serialize(destination=os.path.join(outputDir, "output.trig"), format="trig")




        

def extractMappings(inputMappingFile):
    mappings = []

    with open(inputMappingFile, 'r') as f:
        inputMappings = etree.parse(f)

    namespaces = inputMappings.find("namespaces")
    root = copy.deepcopy(inputMappings)
    toRemove = root.find("mappings")
    toRemove.getparent().remove(toRemove)

    for inputMapping in inputMappings.findall("mappings/mapping"):
        mappings.append(copy.deepcopy(root))
        m = etree.Element("mappings")
        m.append(inputMapping)
        mappings[-1].getroot().append(m)
    return mappings

def performMapping(*, inputDir, mappingFiles, outputDir, generatorFile):
    mappingOutputFiles = []
    inputFiles = [d for d in os.listdir(inputDir) if os.path.isfile(os.path.join(inputDir, d)) and d.endswith(".xml")]
    for inputFile in inputFiles:
        for i, mappingFile in tqdm(enumerate(mappingFiles)):
            mappingOutputFile = os.path.join(outputDir, inputFile[:-4] + "-%s.ttl" % str(i).zfill(MAPPING_ID_ZEROES))
            mappingOutputFiles.append(mappingOutputFile)
            res = os.system("java --add-opens java.base/java.lang.reflect=ALL-UNNAMED \
                --add-opens java.base/java.util=ALL-UNNAMED \
                --add-opens java.base/java.text=ALL-UNNAMED \
                --add-opens java.desktop/java.awt.font=ALL-UNNAMED \
                -jar /x3ml/x3ml-engine.exejar --input %s --x3ml %s --policy %s --format %s --output %s" % 
                            (os.path.join(inputDir, inputFile), 
                            mappingFile,
                            generatorFile,
                            "text/turtle",
                            mappingOutputFile))

    return mappingOutputFiles

def writeIndividualMappingFiles(mappings, dir):
    mappingFiles = []
    for i, mapping in enumerate(mappings):
        filepath = os.path.join(dir, "mapping-%d.x3ml" % i)
        with open(filepath, 'wb') as f:
            f.write(etree.tostring(mapping, pretty_print=True))
            mappingFiles.append(filepath)
    return mappingFiles

mappings = extractMappings(inputMappingFile)

createOrEmptyDirectory(mappingTempDir)
createOrEmptyDirectory(outputTempDir)

mappingFiles = writeIndividualMappingFiles(mappings, mappingDir)
performMapping(inputDir=inputDir, mappingFiles=mappingFiles, outputDir=outputTempDir, generatorFile=generatorFile)

generateOutputGraph(outputDir=outputDir, inputDir=outputTempDir, mappings=mappings)


createOrEmptyDirectory(mappingTempDir)
createOrEmptyDirectory(outputTempDir)
import hashlib
import xml.etree.ElementTree as ET
from abc import abstractmethod

class AbstractStrategy:

    @abstractmethod
    def transform(self, elements, type, textId):
        pass

    def processCategories(self, annotationBlock, element, isAnnotationBlockNew):
        if not isAnnotationBlockNew:
            return

        if 'wikipediaExternalRef' not in element:
            return

        textClass = ET.SubElement(annotationBlock, "textClass", attrib={"type": "categories"})

        wikipedia_external_ref = element['wikipediaExternalRef']

        concept, status_code = self.nerdClient.fetch_concept(wikipedia_external_ref)

        if 'categories' in concept:
            keywords = ET.SubElement(textClass, "keywords")
            for category in concept['categories']:
                ET.SubElement(keywords, "term",
                              attrib={
                                  'scheme': category['source'],
                                  'key': str(category["page_id"])
                              }
                              ).text = category['category']

    def processDomains(self, annotationBlock, element, isAnnotationBlockNew):
        if not isAnnotationBlockNew:
            return

        textClass = ET.SubElement(annotationBlock, "textClass", attrib={"type": "domains"})

        if 'domains' in element:
            keywords = ET.SubElement(textClass, "keywords")
            for domain in element['domains']:
                ET.SubElement(keywords, "term").text = str(domain)

    def processDefinitions(self, parentBlock, element, isAnnotationBlockNew):
        if not isAnnotationBlockNew:
            return

        if 'definitions' in concept:
            for definition in concept['definitions']:
                attribs = {}
                if 'source' in definition:
                    attribs = {'resp': definition['source']}

                gloss = ET.SubElement(parentBlock, "gloss", attrib=attribs).text = definition['definition']

    def addIdno(self, element, parent):
        if 'wikipediaExternalRef' in element:
            idno = ET.SubElement(parent, "idno", attrib={'source': 'wikipedia-en'})
            idno.text = element['wikipediaExternalRef']
        elif 'wikidataID' in element:
            idno = ET.SubElement(parent, "idno", attrib={'source': 'wikidata'})
            idno.text = element['wikidataId']

    def populateAnnotationBlock(self, annotationBlock, element, elementId, textId):
        offsetStart = element['offsetStart']
        offsetEnd = element['offsetEnd']
        m = hashlib.md5()
        m.update((str(offsetStart) + ' ' + str(offsetEnd)).encode('utf-8'))
        interpId = m.hexdigest()

        sub_element = ET.SubElement(annotationBlock, "interp", attrib={
            "inst": '#' + interpId,
            "ana": '#' + elementId,
            "cert": str(0.0)
        })

        if 'nerd_selection_score' in element:
            sub_element.attrib['cert'] = str(element['nerd_selection_score'])

        ET.SubElement(annotationBlock, "span", attrib={"xml:id": interpId,
                                                       "from": "#string-range(//p[@xml:id='" + textId + "']," +
                                                               str(offsetStart) + "," +
                                                               str(offsetEnd) + ")"})

    def addTerms(self, element, parent, tagName):
        ET.SubElement(parent, tagName, attrib={'type': 'rawName'}).text = element['rawName']
        if 'preferredTerm' in element:
            ET.SubElement(parent, tagName, attrib={'type': 'preferredTerm'}).text = element['preferredTerm']

    def calculateElementId(self, element):
        m = hashlib.md5()
        m.update(element['rawName'].encode('utf-8'))
        elementId = m.hexdigest()
        return elementId

    def fetchConcept(self, element):
        pass


class LocationStrategy(AbstractStrategy):
    type = "location"

    def transform(self, elements, type, textId):
        idUniqueList = {}

        listAnnotation = ET.Element("listAnnotation",
                                    attrib={"type": str(type).lower()})
        for element in elements:
            elementId = self.calculateElementId(element)
            # print(element['rawName'] + ' -> ' + elementId);

            concept = super(LocationStrategy, self).fetchConcept(element)
            (annotationBlock, isAnnotationBlockNew) = self.generateOrReuseAnnotationBlock(element, concept, elementId,
                                                                                          idUniqueList, listAnnotation)
            self.populateAnnotationBlock(annotationBlock, element, elementId, textId)
            self.processDomains(annotationBlock, element, isAnnotationBlockNew)
            self.processCategories(annotationBlock, element, concept, isAnnotationBlockNew)

        return listAnnotation

    def generateOrReuseAnnotationBlock(self, element, concept, elementId, idUniqueList, listAnnotation):
        if (elementId in idUniqueList.keys()) is False:
            annotationBlock = ET.SubElement(listAnnotation, "annotationBlock", xmlns="http://www.tei-c.org/ns/1.0")
            idUniqueList[elementId] = annotationBlock
            desc = ET.SubElement(annotationBlock, "desc")
            place = ET.SubElement(desc, "place", attrib={"xml:id": elementId})
            self.addTerms(element, place, 'placeName')
            self.addIdno(element, place)
            self.processDefinitions(place, concept, element, True)
            isAnnotationBlockNew = True
        else:
            annotationBlock = idUniqueList[elementId]
            isAnnotationBlockNew = False

        return annotationBlock, isAnnotationBlockNew


class PersonStrategy(AbstractStrategy):
    type = "individuals"

    def transform(self, elements, type, textId):
        idUniqueList = {}

        listAnnotation = ET.Element("listAnnotation",
                                    attrib={"type": str(type).lower()})
        for element in elements:
            elementId = self.calculateElementId(element)
            # print(element['rawName'] + ' -> ' + elementId);

            (annotationBlock, isAnnotationBlockNew) = self.generateOrReuseAnnotationBlock(element, elementId,
                                                                                          idUniqueList, listAnnotation)
            self.populateAnnotationBlock(annotationBlock, element, elementId, textId)
            self.processCategories(annotationBlock, element, isAnnotationBlockNew)
            # self.processDefinitions(annotationBlock, element, isAnnotationBlockNew)
            self.processDomains(annotationBlock, element, isAnnotationBlockNew)

        return listAnnotation

    def generateOrReuseAnnotationBlock(self, element, elementId, idUniqueList, listAnnotation):
        if (elementId in idUniqueList.keys()) is False:
            annotationBlock = ET.SubElement(listAnnotation, "annotationBlock", xmlns="http://www.tei-c.org/ns/1.0")
            idUniqueList[elementId] = annotationBlock
            person = ET.SubElement(annotationBlock, "person", attrib={"xml:id": elementId})
            desc = ET.SubElement(person, "desc")
            self.addTerms(element, desc, 'persName')
            self.addIdno(element, desc)
            self.processDefinitions(person, element, True)
            isAnnotationBlockNew = True
        else:
            annotationBlock = idUniqueList[elementId]
            isAnnotationBlockNew = False

        return annotationBlock, isAnnotationBlockNew


class PeriodStrategy(AbstractStrategy):
    type = "dateTimes"

    def transform(self, elements, type, textId):
        idUniqueList = {}

        listAnnotation = ET.Element("listAnnotation",
                                    attrib={"type": str(type).lower()})
        for element in elements:
            elementId = self.calculateElementId(element)
            # print(element['rawName'] + ' -> ' + elementId);

            (annotationBlock, isAnnotationBlockNew) = self.generateOrReuseAnnotationBlock(element, elementId,
                                                                                          idUniqueList, listAnnotation)
            self.populateAnnotationBlock(annotationBlock, element, elementId, textId)
            self.processCategories(annotationBlock, element, isAnnotationBlockNew)
            # self.processDefinitions(annotationBlock, element, isAnnotationBlockNew)
            self.processDomains(annotationBlock, element, isAnnotationBlockNew)

        return listAnnotation

    def generateOrReuseAnnotationBlock(self, element, elementId, idUniqueList, listAnnotation):
        if (elementId in idUniqueList.keys()) is False:
            annotationBlock = ET.SubElement(listAnnotation, "annotationBlock", xmlns="http://www.tei-c.org/ns/1.0")
            idUniqueList[elementId] = annotationBlock
            desc = ET.SubElement(annotationBlock, "desc")
            date = ET.SubElement(desc, "date", attrib={"xml:id": elementId})
            self.addTerms(element, desc, 'date')
            self.addIdno(element, desc)
            self.processDefinitions(date, element, True)
            isAnnotationBlockNew = True
        else:
            annotationBlock = idUniqueList[elementId]
            isAnnotationBlockNew = False

        return annotationBlock, isAnnotationBlockNew


class EventStrategy(AbstractStrategy):
    type = "event"

    def transform(self, elements, type, textId):
        idUniqueList = {}

        listAnnotation = ET.Element("listAnnotation",
                                    attrib={"type": str(type).lower()})
        for element in elements:
            elementId = self.calculateElementId(element)
            # print(element['rawName'] + ' -> ' + elementId);

            (annotationBlock, isAnnotationBlockNew) = self.generateOrReuseAnnotationBlock(element, elementId,
                                                                                          idUniqueList, listAnnotation)
            self.populateAnnotationBlock(annotationBlock, element, elementId, textId)
            self.processCategories(annotationBlock, element, isAnnotationBlockNew)
            # self.processDefinitions(annotationBlock, element, isAnnotationBlockNew)
            self.processDomains(annotationBlock, element, isAnnotationBlockNew)

        return listAnnotation

    def generateOrReuseAnnotationBlock(self, element, elementId, idUniqueList, listAnnotation):
        if (elementId in idUniqueList.keys()) is False:
            annotationBlock = ET.SubElement(listAnnotation, "annotationBlock", xmlns="http://www.tei-c.org/ns/1.0")
            idUniqueList[elementId] = annotationBlock
            event = ET.SubElement(annotationBlock, "event", attrib={"xml:id": elementId})
            desc = ET.SubElement(event, "desc")
            self.addTerms(element, event, 'term')
            self.addIdno(element, desc)
            self.processDefinitions(event, element, True)
            isAnnotationBlockNew = True
        else:
            annotationBlock = idUniqueList[elementId]
            isAnnotationBlockNew = False

        return annotationBlock, isAnnotationBlockNew

    def processDefinitions(self, parentBlock, element, isAnnotationBlockNew):
        if not isAnnotationBlockNew:
            return

        if 'definitions' in element.keys():
            for definition in element['definitions']:
                attribs = {}
                if 'source' in definition:
                    attribs = {'resp': definition['source']}

                gloss = ET.SubElement(parentBlock, "desc", attrib=attribs).text = definition['definition']


class GenericItemStrategy(AbstractStrategy):
    ###
    # Takes the json element, the root element on which attach the new item and the key
    ###
    def transform(self, elements, type, textId):
        idUniqueList = {}

        listAnnotation = ET.Element("listAnnotation",
                                    attrib={"type": "generic", "subType": str(type).lower()})
        for element in elements:
            elementId = self.calculateElementId(element)
            # print(element['rawName'] + ' -> ' + elementId);

            (annotationBlock, isAnnotationBlockNew) = self.generateOrReuseAnnotationBlock(element, elementId,
                                                                                          idUniqueList, listAnnotation)
            self.populateAnnotationBlock(annotationBlock, element, elementId, textId)
            self.processCategories(annotationBlock, element, isAnnotationBlockNew)
            # self.processDefinitions(annotationBlock, element, isAnnotationBlockNew)
            self.processDomains(annotationBlock, element, isAnnotationBlockNew)

        return listAnnotation

    def generateOrReuseAnnotationBlock(self, element, elementId, idUniqueList, listAnnotation):
        if (elementId in idUniqueList.keys()) is False:
            annotationBlock = ET.SubElement(listAnnotation, "annotationBlock", xmlns="http://www.tei-c.org/ns/1.0")
            idUniqueList[elementId] = annotationBlock
            term = ET.SubElement(annotationBlock, "term", attrib={"xml:id": elementId})
            desc = ET.SubElement(term, "desc")
            self.addTerms(element, desc, 'term')
            self.addIdno(element, desc)
            self.processDefinitions(term, element, True)

            isAnnotationBlockNew = True
        else:
            annotationBlock = idUniqueList[elementId]
            isAnnotationBlockNew = False

        return annotationBlock, isAnnotationBlockNew

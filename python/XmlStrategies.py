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

        textClass = ET.SubElement(annotationBlock, "textClass", attrib={"type": "categories"})
        if 'categories' in element.keys():
            keywords = ET.SubElement(textClass, "keywords")
            for category in element['categories']:
                ET.SubElement(keywords, "term",
                              attrib={
                                  'scheme': category['source'],
                                  'key': str(category["page_id"])
                              }
                              ).text = category['category']

    def processDefinitions(self, parentBlock, element, isAnnotationBlockNew):
        if not isAnnotationBlockNew:
            return

        if 'definitions' in element.keys():
            for definition in element['definitions']:
                attribs = {}
                if 'source' in definition:
                    attribs = {'resp': definition['source']}

                gloss = ET.SubElement(parentBlock, "gloss", attrib=attribs).text = definition['definition']

    def populateAnnotationBlock(self, annotationBlock, element, elementId, textId):
        offsetStart = element['offsetStart']
        offsetEnd = element['offsetEnd']
        m = hashlib.md5()
        m.update((str(offsetStart) + ' ' + str(offsetEnd)).encode('utf-8'))
        interpId = m.hexdigest()
        ET.SubElement(annotationBlock, "interp", attrib={"inst": interpId, "ana": elementId})
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


class LocationStrategy(AbstractStrategy):
    type = "location"

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

        return listAnnotation

    def generateOrReuseAnnotationBlock(self, element, elementId, idUniqueList, listAnnotation):
        if (elementId in idUniqueList.keys()) is False:
            annotationBlock = ET.SubElement(listAnnotation, "annotationBlock", xmlns="http://www.tei-c.org/ns/1.0")
            idUniqueList[elementId] = annotationBlock
            place = ET.SubElement(annotationBlock, "place", attrib={"xml:id": elementId})
            self.addTerms(element, place, 'placeName')
            self.processDefinitions(place, element, True)
            isAnnotationBlockNew = True
        else:
            annotationBlock = idUniqueList[elementId]
            isAnnotationBlockNew = False

        return annotationBlock, isAnnotationBlockNew


class PersonStrategy(AbstractStrategy):
    type = "person"

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

        return listAnnotation

    def generateOrReuseAnnotationBlock(self, element, elementId, idUniqueList, listAnnotation):
        if (elementId in idUniqueList.keys()) is False:
            annotationBlock = ET.SubElement(listAnnotation, "annotationBlock", xmlns="http://www.tei-c.org/ns/1.0")
            idUniqueList[elementId] = annotationBlock
            person = ET.SubElement(annotationBlock, "person", attrib={"xml:id": elementId})
            self.addTerms(element, person, 'persName')
            self.processDefinitions(person, element, True)
            isAnnotationBlockNew = True
        else:
            annotationBlock = idUniqueList[elementId]
            isAnnotationBlockNew = False

        return annotationBlock, isAnnotationBlockNew


class PeriodStrategy(AbstractStrategy):
    type = "period"

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

        return listAnnotation

    def generateOrReuseAnnotationBlock(self, element, elementId, idUniqueList, listAnnotation):
        if (elementId in idUniqueList.keys()) is False:
            annotationBlock = ET.SubElement(listAnnotation, "annotationBlock", xmlns="http://www.tei-c.org/ns/1.0")
            idUniqueList[elementId] = annotationBlock
            date = ET.SubElement(annotationBlock, "date", attrib={"xml:id": elementId})
            self.addTerms(element, annotationBlock, 'date')
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

        return listAnnotation

    def generateOrReuseAnnotationBlock(self, element, elementId, idUniqueList, listAnnotation):
        if (elementId in idUniqueList.keys()) is False:
            annotationBlock = ET.SubElement(listAnnotation, "annotationBlock", xmlns="http://www.tei-c.org/ns/1.0")
            idUniqueList[elementId] = annotationBlock
            event = ET.SubElement(annotationBlock, "event", attrib={"xml:id": elementId})
            self.addTerms(element, event, 'head')
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

        return listAnnotation

    def generateOrReuseAnnotationBlock(self, element, elementId, idUniqueList, listAnnotation):
        if (elementId in idUniqueList.keys()) is False:
            annotationBlock = ET.SubElement(listAnnotation, "annotationBlock", xmlns="http://www.tei-c.org/ns/1.0")
            idUniqueList[elementId] = annotationBlock
            term = ET.SubElement(annotationBlock, "term", attrib={"xml:id": elementId})
            self.addTerms(element, term, 'term')
            self.processDefinitions(term, element, True)
            isAnnotationBlockNew = True
        else:
            annotationBlock = idUniqueList[elementId]
            isAnnotationBlockNew = False

        return annotationBlock, isAnnotationBlockNew

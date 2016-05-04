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

        listBibl = ET.SubElement(annotationBlock, "listBibl", attrib={"type": "categories"})
        if 'categories' in element.keys():
            for category in element['categories']:
                biblStruct = ET.SubElement(listBibl, "biblStruct")

                ET.SubElement(biblStruct, "title").text = category['category']
                ET.SubElement(biblStruct, "publisher").text = category['source']
                ET.SubElement(biblStruct, "idno").text = str(category["page_id"])

    def processDefinitions(self, annotationBlock, element, isAnnotationBlockNew):
        if not isAnnotationBlockNew:
            return

        listBiblDefinitions = ET.SubElement(annotationBlock, "listBibl", attrib={"type": "definitions"})
        if 'definitions' in element.keys():
            for category in element['definitions']:
                ET.SubElement(listBiblDefinitions, "bibl").text = category['definition']

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
            self.processDefinitions(annotationBlock, element, isAnnotationBlockNew)

        return listAnnotation

    def generateOrReuseAnnotationBlock(self, element, elementId, idUniqueList, listAnnotation):
        if (elementId in idUniqueList.keys()) is False:
            annotationBlock = ET.SubElement(listAnnotation, "annotationBlock", xmlns="http://www.tei-c.org/ns/1.0")
            idUniqueList[elementId] = annotationBlock
            person = ET.SubElement(annotationBlock, "place", attrib={"xml:id": elementId})
            ET.SubElement(person, "placeName").text = element['rawName']
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
            self.processDefinitions(annotationBlock, element, isAnnotationBlockNew)

        return listAnnotation


def generateOrReuseAnnotationBlock(self, element, elementId, idUniqueList, listAnnotation):
    if (elementId in idUniqueList.keys()) is False:
        annotationBlock = ET.SubElement(listAnnotation, "annotationBlock", xmlns="http://www.tei-c.org/ns/1.0")
        idUniqueList[elementId] = annotationBlock
        person = ET.SubElement(annotationBlock, "person", attrib={"xml:id": elementId})
        ET.SubElement(person, "persName").text = element['rawName']
        isAnnotationBlockNew = True
    else:
        annotationBlock = idUniqueList[elementId]
        isAnnotationBlockNew = False

    return annotationBlock, isAnnotationBlockNew


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
            self.processDefinitions(annotationBlock, element, isAnnotationBlockNew)

        return listAnnotation

    def generateOrReuseAnnotationBlock(self, element, elementId, idUniqueList, listAnnotation):
        if (elementId in idUniqueList.keys()) is False:
            annotationBlock = ET.SubElement(listAnnotation, "annotationBlock", xmlns="http://www.tei-c.org/ns/1.0")
            idUniqueList[elementId] = annotationBlock
            ET.SubElement(annotationBlock, "p", attrib={"xml:id": elementId}).text = element['rawName']
            isAnnotationBlockNew = True
        else:
            annotationBlock = idUniqueList[elementId]
            isAnnotationBlockNew = False

        return annotationBlock, isAnnotationBlockNew

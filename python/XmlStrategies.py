import hashlib
import xml.etree.ElementTree as ET
from abc import abstractmethod


class AbstractStrategy:
    @abstractmethod
    def transform(self, json, rootElement):
        pass


class LocationStrategy(AbstractStrategy):
    type = "location"

    def transform(self, json, rootElement):
        pass


class PersonStrategy(AbstractStrategy):
    type = "person"

    def transform(self, json, rootElement):
        pass


class GenericItemStrategy(AbstractStrategy):
    ###
    # Takes the json element, the root element on which attach the new item and the key
    ###
    def transform(self, elements, type, textId):
        idUniqueList = {}

        listAnnotation = ET.Element("listAnnotation",
                                    attrib={"type": "generic", "subType": str(type).lower()})
        for element in elements:
            m = hashlib.md5()
            m.update(element['rawName'].encode('utf-8'))
            elementId = m.hexdigest()
            # print(element['rawName'] + ' -> ' + elementId);

            if (elementId in idUniqueList.keys()) is False:
                annotationBlock = ET.SubElement(listAnnotation, "annotationBlock", xmlns="http://www.tei-c.org/ns/1.0")
                idUniqueList[elementId] = annotationBlock
                ET.SubElement(annotationBlock, "p", attrib={"xml:id": elementId}).text = element['rawName']
            else:
                annotationBlock = idUniqueList[elementId]

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

        return listAnnotation

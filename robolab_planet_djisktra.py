#!/usr/bin/env python3

# Attention: Do not import the ev3dev.ev3 module in this file
from enum import IntEnum, unique
from typing import List, Tuple, Dict, Union
import math

@unique
class Direction(IntEnum):
    """ Directions in shortcut """
    NORTH = 0
    EAST = 90
    SOUTH = 180
    WEST = 270


Weight = int
"""
Weight of a given path (received from the server)

Value:  -1 if blocked path
        >0 for all other paths
        never 0
"""


class Knot: #Knoten
    """
    ein Knot hat 3 Attributen:
    Knot.knot: [(Int, Int), [Int, Int], [Int, Int], [Int, Int], [Int, Int]]
                [(Koordinate), [nordlicher Knots Index, Entfernung], [ostlicher Knots Index, Entfernung], [suedlicher Knots Index, Entfernung], [westlicher Knots Index, Entfernung]]
    Knot.predecessor: Koordinate vom Knoten, wodurch er Pfad am kurzesten ist (Dijasktra relevant)
    Knot.abstand: kürzeste Pfadlänge zu diesem Knoten (Dijasktra relevent)
    """
    def __init__(self, koordinate: Tuple[int, int]):

        koordinate = koordinate
        nord = ["unknown Knot", "unknown length"]
        east = ["unknown Knot", "unknown length"]
        south = ["unknown Knot", "unknown length"]
        west = ["unknown Knot", "unknown length"]

        self.knot = [koordinate, nord, east, south, west]
        self.predecessor = None
        self.abstand = math.inf

class Planet:

    def __init__(self):
        #Planet ist ein Behälter von 3 Listen, die jeweils jedes Attribut vom Knot enthalten
        self.knotenliste = []
        self.abstandliste = []
        self.predecessorliste = []

    def add_knot(self, coord): #ein Knot im Planet hinzufügen, diese Funktion wird automatisch aufgeruft in add_path
        vertex = Knot(coord)
        self.knotenliste.append(vertex.knot)
        self.abstandliste.append(vertex.abstand)
        self.predecessorliste.append(vertex.predecessor)

    def add_path(self, start: Tuple[Tuple[int, int], Direction], target: Tuple[Tuple[int, int], Direction],
                 weight: int):
        """
        Schritte:
        Blockierungskontrolle: if weight = -1 (also blockiert), weight zu math.inf gewechselt
        Warum? weil wenn man -1 lässt, Djiasktra Algorithmus sucht immer kleinste Zahl, das führt dazu, dass blockierte Pfade werden immer mitgerechnet

        1) Überprüfen, ob ein Knot hinzugefügt werden muss (im Fall der Knote beim Aufruf der add_path Funktion noch unbekannt ist)
        2) Für start Knot: finde Startknoten.knot in knotenliste und dementsprechende Targetknoten und Entfernung eintragen
        3) Für target Knot: finde Targetknoten.knote in knotenliste und dementsprechende Targetknoten und Entfernung eintragen

        Einige Eigenschaften von add_path:
        -Wenn der Pfad schon bekannt ist (schon 1 oder mehrmals per add_path aufgeruft), beim nächsten Aufruf für den selben Pfad, wird dieser Pfad aktualisiert, wird kein neuer Pfad hinzugefügt
        -Das neu konstruktierte Knot existiert nur im Scope des Aufrufs und nach dem Aufruf wird gelöscht, aber seine Attributen werden kopiert und im Planet eingetragen
        """

        #Blockierungskontrolle

        if weight == -1:
            weight = math.inf

        #Schritt 1
        if all(elem[0] != start[0] for elem in self.knotenliste) and all(elem[0] != target[0] for elem in self.knotenliste):
            self.add_knot(start[0])
            self.add_knot(target[0])

        if any(elem[0] == target[0] for elem in self.knotenliste) and all(elem[0] != start[0] for elem in self.knotenliste):
            self.add_knot(start[0])

        if any(elem[0] == start[0] for elem in self.knotenliste) and all(elem[0] != target[0] for elem in self.knotenliste):
            self.add_knot(target[0])

        #Schritt 2 und 3

        #festellen wer/wo sind die target und start
        Startpunkt = None
        Endpunkt = None
        for i in range(len(self.knotenliste)):
            if self.knotenliste[i][0] == start[0]:
                Startpunkt = self.knotenliste[i]
            if self.knotenliste[i][0] == target[0]:
                Endpunkt = self.knotenliste[i]

        startindex = None
        endindex = None
        #festellen Ausfahrtrichtung
        if start[1] == 0:
            startindex = 1
        if start[1] == 90:
            startindex = 2
        if start[1] == 180:
            startindex = 3
        if start[1] == 270:
            startindex = 4
        #festellen Einfahrtrichtung
        if target[1] == 0:
            endindex = 1
        if target[1] == 90:
            endindex = 2
        if target[1] == 180:
            endindex = 3
        if target[1] == 270:
            endindex = 4
        #und eintragen in entsprechenden Indexen
        Startpunkt[startindex] = [self.knotenliste.index(Endpunkt), weight]
        Endpunkt[endindex] = [self.knotenliste.index(Startpunkt), weight]

    def get_paths(self) -> Dict[Tuple[int, int], Dict[Direction, Tuple[Tuple[int, int], Direction, Weight]]]:

        kantendict = {}

        for element in self.knotenliste:
            coordination = element[0]
            insidedict = {}
            #jeder Knoten wird betrachtet, und insidedict gibt die von diesem Knoten auslaufende Kante an
            for i in range(1, len(element)):
                hindirection = None
                herdirection = None

                if element[i] != [None, None] and element[i] != ["unknown Knot", "unknown length"]: #only need the existierende Kanten
                    if i == 1: #in welche Richtung geht die Kante raus?
                        hindirection = Direction.NORTH
                    if i == 2:
                        hindirection = Direction.EAST
                    if i == 3:
                        hindirection = Direction.SOUTH
                    if i == 4:
                        hindirection = Direction.WEST

                    entfernung = element[i][1]      #Entfernung der Kante
                    hinindex = element[i][0]        #wo kommt die Kante hin?

                    hinknot = self.knotenliste[hinindex][0] #hier kriegt man die Hinknoten
                    for hinelement in self.knotenliste:
                        if self.knotenliste.index(hinelement) == hinindex:
                            for j in range(1, len(hinelement)):
                                if hinelement[j][0] == self.knotenliste.index(element):
                                    if hinelement[0] == element[0]:
                                        if j == 1 and j != i:
                                            herdirection = Direction.NORTH
                                        if j == 2 and j != i:
                                            herdirection = Direction.EAST
                                        if j == 3 and j != i:
                                            herdirection = Direction.SOUTH
                                        if j == 4 and j != i:
                                            herdirection = Direction.WEST
                                    elif hinelement[0] != element[0]:
                                        if j == 1:
                                            herdirection = Direction.NORTH
                                        if j == 2:
                                            herdirection = Direction.EAST
                                        if j == 3:
                                            herdirection = Direction.SOUTH
                                        if j == 4:
                                            herdirection = Direction.WEST

                    insidedict.update({hindirection: (hinknot, herdirection, entfernung)})
                    kantendict.update({coordination: insidedict})
        return kantendict

    def shortest_path(self, start: Tuple[int, int], target: Tuple[int, int]) -> Union[None, List[Tuple[Tuple[int, int], Direction]]]:
        """
        Dijasktra Algorithmus

        Spezialfall 1:
        if target is not in Planet, return an empty path

        Spezialfall 2:
        if planet nicht zusammenhängend ist, return an empty path (wird im Normalfall abgeleitet)

        Normalfall Schritte:
        1) Dijasktra Initialisierung:
            Q ist die Liste der Knoten, die noch zu betrachten im Algorithmus ist
            Abstandwert für Anfangsknoten als 0 initializieren
            Abstandwert für alle anderen Knoten als math.inf wurde initializiert in add_path
            Predecessor für jeden Knoten wurden als None initialisziert in add_path

        2) Solange Liste Q nicht leer ist:
            in jedem Durchlauf wird  in Q ein Knoten mit kleinstem Abstand ausgewählt, und vergleichen, und aktualisieren die Werte Abstand und Predecessor jedes Knotens
            nach jedem Durchlauf wird in Q ein Knoten mit kleinstem Abstand gelöscht

        3) Pfad ausgeben mithilfe Predecessor-Liste und dementsprechen Richtungen aus knotenliste

        4) Abstandwert als math.inf und Predecessorwert als None vorbereiten für den nächsten Aufruf der Funktion

        5) Return Pfad
        """

        #Spezialfall 1
        listtoreturn = []
        kantendict = self.get_paths()
        if target not in kantendict.keys():
            return listtoreturn

        #Schritt 1
        Q = []
        for i in range(len(self.knotenliste)):
            Q.append(i)
            if self.knotenliste[i][0] == start:
                self.abstandliste[i] = 0
        #Schritt 2
        while len(Q) > 0:
            smallestnumber = self.abstandliste[Q[0]]
            takethisindex = Q[0]
            if len(Q) > 0:
                for restknot in Q:
                    if self.abstandliste[restknot] < smallestnumber:
                        smallestnumber = self.abstandliste[restknot]
                        takethisindex = restknot

            minindex = takethisindex
            Q.remove(minindex)

            for inercount in range(1, len(self.knotenliste[minindex])):
                if self.knotenliste[minindex][inercount] != [None, None] and self.knotenliste[minindex][inercount][0] != "unknown Knot" and self.knotenliste[minindex][inercount][0] in Q:
                    alternative = self.abstandliste[minindex] + self.knotenliste[minindex][inercount][1]
                    if alternative < self.abstandliste[self.knotenliste[minindex][inercount][0]]:
                        self.abstandliste[self.knotenliste[minindex][inercount][0]] = alternative
                        self.predecessorliste[self.knotenliste[minindex][inercount][0]] = self.knotenliste[minindex][0]

        #Schritt 3
        hinrichtung = None
        endtuple = target
        while endtuple != start and endtuple != None:
            for elem in self.knotenliste:
                if elem[0] == endtuple:
                    targetindex = self.knotenliste.index(elem)
                    for findpred in self.knotenliste:
                        if findpred[0] == self.predecessorliste[targetindex]:
                            for anotherindex in range(1, len(findpred)):
                                if findpred[anotherindex][0] == self.knotenliste.index(elem):
                                    if anotherindex == 1:
                                        hinrichtung = Direction.NORTH
                                    if anotherindex == 2:
                                        hinrichtung = Direction.EAST
                                    if anotherindex == 3:
                                        hinrichtung = Direction.SOUTH
                                    if anotherindex == 4:
                                        hinrichtung = Direction.WEST
                    if self.predecessorliste[targetindex] != None:
                        listtoreturn.append((self.predecessorliste[targetindex],hinrichtung))
                    endtuple = self.predecessorliste[targetindex]
        #Schritt 4
        self.abstandliste = [math.inf for elemen in self.abstandliste]
        self.predecessorliste = [None for elem in self.predecessorliste]

        #Schritt 5
        listtoreturn.reverse()
        print(listtoreturn)
        return listtoreturn

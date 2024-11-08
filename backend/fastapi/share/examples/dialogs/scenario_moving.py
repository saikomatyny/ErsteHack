#!/usr/bin/python
# -*- coding: utf-8 -*-
"""This test scenario can be invoked either as a standalone Python script or
through the dialog_test executable.
"""

import logging
logger = logging.getLogger('dialogs')
logger.setLevel(logging.DEBUG)
log_handler = logging.StreamHandler()
formatter = logging.Formatter("%(message)s")
log_handler.setFormatter(formatter)
logger.addHandler(log_handler)

import unittest
from dialogs.dialog_core import Dialog
from dialogs.resources_manager import ResourcePool

#By default, use a remote knowledge base
embeddedkb = False
kb_HOST = 'localhost'
kb_PORT = 6969

ResourcePool().init(kb_host = kb_HOST, kb_port = kb_PORT, embeddedkb = embeddedkb, defaultontology = None)

class TestMovingToLondonScenario(unittest.TestCase):
    """
    Scenario
    --------
    ACHILLE and JULIE are moving from Toulouse to London, and they must
    pack everything before leaving. ACHILLE is sorting its video tapes, and he 
    throws away the oldest ones. Jido is watching him.

    Setup:
      One trashbin, one cardboard box, 2 tapes on the table [TAPE1 = Lord of 
      the Robots (lotr) and TAPE2 = JIDO-E].
    
    Complete scenario here:
    http://homepages.laas.fr/slemaign/wiki/doku.php?id=scenario_demo_roman
    """
    
    def setUp(self):
        self.dialog = Dialog()
        self.dialog.start()
        
        self.oro = ResourcePool().ontology_server
        
        try:
            
            self.oro.add([  'ACHILLE rdf:type Human',
                            'ACHILLE rdfs:label Achille',
                            'JULIE rdf:type Human', 
                            'JULIE rdfs:label Julie',
                            'TABLE rdf:type Table',
                            'Trashbin rdfs:subClassOf Box',
                            'CardBoardBox rdfs:subClassOf Box',
                            'CardBoardBox rdfs:label "cardboard box"',
                            'TRASHBIN rdf:type Trashbin',
                            'CARDBOARD_BOX rdf:type CardBoardBox',
                            'CARDBOARD_BOX isOn TABLE',
                            'TAPE1 rdf:type VideoTape', 
                            'TAPE1 rdfs:label "The Lords of the robots"', 
                            'TAPE1 isOn TABLE',
                            'TAPE2 rdf:type VideoTape', 
                            'TAPE2 rdfs:label "Jido-E"', 
                            'TAPE2 isOn TABLE',
                            'VideoTape owl:equivalentClass Tape',
                            'TAPE1 owl:differentFrom TAPE2',
                            ])
            """           
            self.oro.addForAgent('ACHILLE',
                        ['BLUE_TRASHBIN rdf:type Trashbin',
                        'PINK_TRASHBIN rdf:type Trashbin',
                        'BLACK_TAPE rdf:type VideoTape', 'BLACK_TAPE isIn PINK_TRASHBIN',
                        'GREY_TAPE rdf:type VideoTape', 'GREY_TAPE isOn HRP2TABLE'])
            """        
        except AttributeError: #the ontology server is not started of doesn't know the method
            print("Couldn't connect to the ontology server. Aborting the test.")
            raise
        
        try:
            self.oro.addForAgent('ACHILLE',[
                            'ACHILLE rdf:type Human',
                            'ACHILLE rdfs:label Achille',
                            'JULIE rdf:type Human', 
                            'JULIE rdfs:label Julie',
                            'TABLE rdf:type Table',
                            'Trashbin rdfs:subClassOf Box',
                            'CardBoardBox rdfs:subClassOf Box',
                            'CardBoardBox rdfs:label "cardboard box"',
                            'TRASHBIN rdf:type Trashbin',
                            'CARDBOARD_BOX rdf:type CardBoardBox',
                            'CARDBOARD_BOX isOn TABLE',
                            'TAPE1 rdf:type VideoTape', 
                            'TAPE1 rdfs:label "The Lords of the robots"', 
                            'TAPE1 isOn TABLE',
                            'TAPE2 rdf:type VideoTape', 
                            'TAPE2 rdfs:label "Jido-E"', 
                            'TAPE2 isOn TABLE',
                            
                            'VideoTape owl:equivalentClass Tape',
                            
                            'TAPE1 owl:differentFrom TAPE2',
                            ])
        except AttributeError: #the ontology server is not started of doesn't know the method
            print("Couldn't connect to the ontology server. Aborting the test.")
            raise
        
        
        try:
            self.oro.addForAgent('JULIE',[
                            'ACHILLE rdf:type Human',
                            'ACHILLE rdfs:label Achille',
                            'JULIE rdf:type Human', 
                            'JULIE rdfs:label Julie',
                            'TABLE rdf:type Table',
                            'Trashbin rdfs:subClassOf Box',
                            'CardBoardBox rdfs:subClassOf Box',
                            'CardBoardBox rdfs:label "cardboard box"',
                            'TRASHBIN rdf:type Trashbin',
                            'CARDBOARD_BOX rdf:type CardBoardBox',
                            'CARDBOARD_BOX isOn TABLE',
                            'TAPE1 rdf:type VideoTape', 
                            'TAPE1 rdfs:label "The Lords of the robots"', 
                            'TAPE1 isOn TABLE',
                            'TAPE2 rdf:type VideoTape', 
                            'TAPE2 rdfs:label "Jido-E"', 
                            'TAPE2 isOn TABLE',
                            
                            'VideoTape owl:equivalentClass Tape',
                            
                            'TAPE1 owl:differentFrom TAPE2',
                            ])
        except AttributeError: #the ontology server is not started of doesn't know the method
            print("Couldn't connect to the ontology server. Aborting the test.")
            raise
       
            
    def runTest(self):
        """ MOVING TO LONDON SCENARIO
        
        ACHILLE puts TAPE1 in CARDBOARDBOX"""

        print()
        self.oro.add(['TAPE1 isIn CARDBOARD_BOX'])
        self.oro.addForAgent('ACHILLE',['ACHILLE pointsAt CARDBOARD_BOX'])
        
        stmt = "Jido, what is in the box?"
        answer = "This box"
        ####
        res = self.dialog.test('ACHILLE', stmt, answer)
        self.assertEqual(res[1][1],"The Lords of the robots.")
        
        self.oro.removeForAgent('ACHILLE',['ACHILLE pointsAt CARDBOARD_BOX'])
        
        stmt = "Ok. And where is the other tape?"
        ####
        self.assertEqual(self.dialog.test('ACHILLE', stmt)[1][1],"The other tape is on the table.")
        
        stmt = "Ok. Thanks."
        self.assertEqual(self.dialog.test('ACHILLE', stmt)[1][1],"You're welcome.")
        
        """Julie arrives, and gives two big boxes to ACHILLE. He can not take anything!"""
       
        self.oro.update(['TAPE2 isReachable false'])
                            
        stmt = "Jido, can you take Jido-E?"
        ####
        res = self.dialog.test('ACHILLE', stmt)
        
        expected_result = ['ACHILLE desires *',
                  '* rdf:type Get',
                  '* performedBy myself',
                  '* actsOnObject TAPE2']
        
        self.assertTrue(check_results(res[0], expected_result))
        
        """Julie pushes a bit the TAPE2, which is now close enough, but still 
        unreachable because of an obstacle.
        """
        self.oro.addForAgent('ACHILLE',['ACHILLE pointsAt TAPE2'])
        stmt = "And now, can you reach this tape?"
        ####
        ### Check ['myself reaches TAPE2']
        self.assertEqual(self.dialog.test('ACHILLE', stmt)[1][1],"I don't know, if I can reach this tape now.")
        self.oro.removeForAgent('ACHILLE',['ACHILLE pointsAt TAPE2'])
        
        """Julie pushes again the tape. It is now reachable.
        """
        self.oro.update(['TAPE2 isReachable true'])
        
        stmt = "Jido, can you take it?"
        ####
        ### Do you mean Jido-E
        answer = "I mean Jido-E"
        ###
        res = self.dialog.test('JULIE', stmt, answer)
        expected_result = ['JULIE desires *',
                  '* rdf:type Get',
                  '* performedBy myself',
                  '* actsOnObject TAPE2']
        
        self.assertTrue(check_results(res[0], expected_result))
        
        """Achille puts JIDO-E in the trashbin. Jido still observes. Achille 
        leaves. Julie finds JIDO-E in the trashbin, and takes it away. ACHILLE 
        comes back to the table.
        """

        print()
        self.oro.remove(['TAPE2 isOn TABLE'])
        self.oro.add(['TAPE2 isAt JULIE'])
        self.oro.addForAgent('ACHILLE', ['TAPE2 isIn TRASHBIN'])
                            
        stmt = "Can you give me the tape in the trashbin?"
        #Expected intermediate question: "You mean, the JIDO-E tape?"
        #NOT FOR ROMAN demo!
        #answer = "Yes"
        ####
        res = self.dialog.test('ACHILLE', stmt)
        
        expected_result = ['ACHILLE desires *',
                  '* rdf:type Give',
                  '* performedBy myself',
                  '* actsOnObject TAPE2',
                  '* receivedBy ACHILLE']
        
        self.assertTrue(check_results(res[0], expected_result))

    def tearDown(self):
        self.dialog.stop()
        self.dialog.join()


def check_results(res, expected):
    def check_triplets(tr , te):
        tr_split = tr.split()
        te_split = te.split()
        
        return  (not '?' in tr_split[0]) and \
                (not '?' in tr_split[2]) and \
                (tr_split[0] == te_split[0] or te_split[0] == '*') and\
                (tr_split[1] == te_split[1]) and\
                (tr_split[2] == te_split[2] or te_split[2] == '*') 
       
    while res:
        r = res.pop()
        for e in expected:
            if check_triplets(r, e):
                expected.remove(e)
    if expected:
        logger.info("\t**** /Missing statements in result:   ")
        logger.info("\t" + str(expected) + "\n")
           
    return expected == res
    
def test_suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestMovingToLondonScenario)
    
    return suite
    
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(test_suite())

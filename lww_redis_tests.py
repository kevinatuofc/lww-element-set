"""unit tests for the lww_redis"""

import unittest
import redis
from lww_redis import LWW_redis as LWW_set
import threading
import random

r = redis.StrictRedis(host='localhost', port=6379, db=0)

class Test_LWW_Redis(unittest.TestCase):
    def setUp(self):
        #print "Clearing up lww_add_set and remove set before test"
        r.zremrangebyrank('lww_add_set',0,-1)
        r.zremrangebyrank('lww_remove_set',0,-1)
        self.a = random.randint(1,100)  # a random number each time

    def tearDown(self):
        #print "Clearing up lww_add_set and remove set after test"
        r.zremrangebyrank('lww_add_set',0,-1)
        r.zremrangebyrank('lww_remove_set',0,-1)

    def test1(self):
        lww = LWW_set(r)
        lww.add(self.a,1)
        self.assertTrue(lww.exist(self.a))
        lww.add(self.a,0)
        self.assertTrue(lww.exist(self.a))
        expected_arr = [str(self.a),]
        self.assertEqual(lww.get(), expected_arr)

    def test2(self):
        lww = LWW_set(r)
        lww.add(self.a,1)
        self.assertTrue(lww.exist(self.a))
        lww.add(self.a,1)
        self.assertTrue(lww.exist(self.a))
        expected_arr = [str(self.a),]
        self.assertEqual(lww.get(), expected_arr)

    def test3(self):
        lww = LWW_set(r)
        lww.add(self.a,1)
        self.assertTrue(lww.exist(self.a))
        lww.add(self.a,2)
        self.assertTrue(lww.exist(self.a))
        expected_arr = [str(self.a),]
        self.assertEqual(lww.get(), expected_arr)

    def test4(self):
        lww = LWW_set(r)
        lww.remove(self.a,1)
        self.assertFalse(lww.exist(self.a))
        lww.add(self.a,0)
        self.assertFalse(lww.exist(self.a))
        expected_arr = []
        self.assertEqual(lww.get(), expected_arr)

    def test5(self):
        lww = LWW_set(r)
        lww.remove(self.a,1)
        self.assertFalse(lww.exist(self.a))
        lww.add(self.a,1)
        self.assertTrue(lww.exist(self.a))
        expected_arr = [str(self.a),]
        self.assertEqual(lww.get(), expected_arr)

    def test6(self):
        lww = LWW_set(r)
        lww.remove(self.a,1)
        self.assertFalse(lww.exist(self.a))
        lww.add(self.a,2)
        self.assertTrue(lww.exist(self.a))
        expected_arr = [str(self.a),]
        self.assertEqual(lww.get(), expected_arr)

    def test7(self):
        lww = LWW_set(r)
        lww.remove(self.a,1)
        self.assertFalse(lww.exist(self.a))
        lww.remove(self.a,0)
        self.assertFalse(lww.exist(self.a))
        expected_arr = []
        self.assertEqual(lww.get(), expected_arr)

    def test8(self):
        lww = LWW_set(r)
        lww.remove(self.a,1)
        self.assertFalse(lww.exist(self.a))
        lww.remove(self.a,1)
        self.assertFalse(lww.exist(self.a))
        expected_arr = []
        self.assertEqual(lww.get(), expected_arr)

    def test8(self):
        lww = LWW_set(r)
        lww.remove(self.a,1)
        self.assertFalse(lww.exist(self.a))
        lww.remove(self.a,2)
        self.assertFalse(lww.exist(self.a))
        expected_arr = []
        self.assertEqual(lww.get(), expected_arr)

    def test9(self):
        lww = LWW_set(r)
        lww.remove(self.a,1)
        self.assertFalse(lww.exist(self.a))
        lww.remove(self.a,0)
        self.assertFalse(lww.exist(self.a))
        expected_arr = []
        self.assertEqual(lww.get(), expected_arr)

    def test10(self):
        lww = LWW_set(r)
        lww.add(self.a,1)
        self.assertTrue(lww.exist(self.a))
        lww.remove(self.a,0)
        self.assertTrue(lww.exist(self.a))
        expected_arr = [str(self.a),]
        self.assertEqual(lww.get(), expected_arr)

    def test11(self):
        lww = LWW_set(r)
        lww.add(self.a,1)
        self.assertTrue(lww.exist(self.a))
        lww.remove(self.a,1)
        self.assertTrue(lww.exist(self.a))
        expected_arr = [str(self.a),]
        self.assertEqual(lww.get(), expected_arr)

    def test12(self):
        lww = LWW_set(r)
        lww.add(self.a,1)
        self.assertTrue(lww.exist(self.a))
        lww.remove(self.a,2)
        self.assertFalse(lww.exist(self.a))
        expected_arr = []
        self.assertEqual(lww.get(), expected_arr)

    def test_string_add_remove(self):
        lww = LWW_set(r)
        a = "s1"
        b = "s22"
        lww.add(a,1)
        self.assertTrue(lww.exist(a))
        self.assertFalse(lww.exist(b))
        lww.add(b,1)
        lww.remove(a, 2)
        self.assertTrue(lww.exist(b))
        self.assertFalse(lww.exist(a))
        expected_arr = [b,]
        self.assertEqual(lww.get(), expected_arr)

    def test_multi_threaded(self):
        """Uses mutiple add/remove threads to test an lww-set object."""

        lww = LWW_set(r)
        base = [1,2,3,4]       
        element = 2
        nTests = 100
        for i in range(nTests):
            threads = []
            # For every test round, we increase the timestamp
            timestamps = base * (i+1) 
            
            # remove timestamp3 is always largest. add timestamp is always second
            remove_timestamp1 = timestamps[0]
            remove_timestamp2 = timestamps[1]
            add_timestamp = timestamps[2]
            remove_timestamp3 = timestamps[3]

            addThread = AddThread(lww, element, add_timestamp)
            removeThread1 = RemoveThread(lww, element, remove_timestamp1)
            removeThread2 = RemoveThread(lww, element, remove_timestamp2)
            removeThread3 = RemoveThread(lww, element, remove_timestamp3)

            threads.append(removeThread1)
            threads.append(removeThread2)            
            threads.append(removeThread3)
            threads.append(addThread)

            for t in threads:
                t.start()

            for t in threads:
                t.join()
            
            # Since only removeThread1 has the higher than the add thread,
            # eventually the element will be removed. 
            # If there is any race condition, i.e., one old remove thread
            # overwrites a new one, then the below assertion may fail. 
            self.assertFalse(lww.exist(element))


class AddThread (threading.Thread):
    def __init__(self, lww_set, element, timestamp):
        threading.Thread.__init__(self)
        self.lww_set = lww_set
        self.timestamp = timestamp
        self.element = element
    def run(self):
        self.lww_set.add(self.element, self.timestamp)

class RemoveThread (threading.Thread):
    def __init__(self, lww_set, element, timestamp):
        threading.Thread.__init__(self)
        self.lww_set = lww_set
        self.timestamp = timestamp
        self.element = element
    def run(self):
        self.lww_set.remove(self.element, self.timestamp)

        
if __name__ == '__main__':
    unittest.main()


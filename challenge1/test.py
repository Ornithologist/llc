import unittest
from garage import Garage
from random import randint
from concurrent.futures import ThreadPoolExecutor, as_completed

HALF_AN_HR = 30 * 60
ONE_HR = 60 * 60

def ask_for_parking_lot(garage, duration_sec):
    return garage.get_parking_lot(duration_sec)

class GarageTest(unittest.TestCase):

    def test_linear(self):
        k = 100
        my_garage = Garage(k)
        for i in range(k):
            duration_sec = randint(HALF_AN_HR, ONE_HR)
            lid, ts = my_garage.get_parking_lot(duration_sec)
            self.assertNotEqual(lid, -1)

        duration_sec = randint(HALF_AN_HR, ONE_HR)
        lid, ts = my_garage.get_parking_lot(duration_sec)
        self.assertEqual(lid, -1)

    def test_threading(self):
        k = 100
        total = 150
        my_garage = Garage(k)

        success_count = 0
        failure_count = 0
        with ThreadPoolExecutor(max_workers=total) as executor:
            # create tasks
            futures = [
                executor.submit(
                    ask_for_parking_lot, my_garage, randint(HALF_AN_HR, ONE_HR))
                for _ in range(total)
            ]
            # assert collectively
            for i, f in enumerate(as_completed(futures)):
                lid, ts = f.result()
                if lid == -1:
                    failure_count += 1
                else:
                    success_count += 1
        self.assertEqual(success_count, 100)
        self.assertEqual(failure_count, 50)


if __name__ == '__main__':
    unittest.main()

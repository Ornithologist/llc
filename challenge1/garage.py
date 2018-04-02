'''
Garage is a collection of parking lots that share the same booking interface;
Supported APIs are:
    get_parking_lot(duration_sec)

A Garage instance is supposed to be used as a singleton when all parking lots
belong to a single place geographically.
In cases of (geo-)distributed parking lots, each Garage instance can be labelled
with geographic coordinates and be used as a intermediate interface for parking
lot booking.
'''

import time
from queue import PriorityQueue


class ParkingLot(object):
    '''
    A ParkingLot is available for one vehicle for booking at one time.
    A vehicle can enter and leave multiple times in its time of booking, thus
    early exit does not free-up the allocated time window.
    @param lid: integer, lot number

    Supported APIs are:
    get_next_opening(ts)
    add_new_booking(ts, duration_sec)

    A ParkingLot with a smaller lot number and a earlier next opening would be
    considered earlier upon a booking request
    '''

    def __init__(self, lid):
        '''
        @attribute lid: the parking lot number, integer
        @attribute bookings: a list of booking start time in unix epoch
        @attribute next_opening: unix epoch of the earliest available time
        '''
        self.lid = lid
        self.bookings = []
        self.next_opening = 0  # zero if no exiting bookings

    def __eq__(self, other):
        return (self.lid == other.lid)

    def __ne__(self, other):
        return (self.lid == other.lid)

    def __lt__(self, other):
        return (self.next_opening < other.next_opening or
                (self.next_opening == other.next_opening and
                 self.lid < other.lid))

    def __le__(self, other):
        return (self.next_opening < other.next_opening or
                (self.next_opening == other.next_opening and
                 self.lid <= other.lid))

    def __gt__(self, other):
        return (self.next_opening > other.next_opening or
                (self.next_opening == other.next_opening and
                 self.lid > other.lid))

    def __ge__(self, other):
        return (self.next_opening > other.next_opening or
                (self.next_opening == other.next_opening and
                 self.lid >= other.lid))

    def __repr__(self):
        return "lot_number=%s next_opening=%s" % (self.lid, self.next_opening)

    def get_next_opening(self, ts):
        '''
        get next earliest opening(in unix epoch) no earlier than * ts*
        @param ts: unix epoch of the desired time, typically current clock value
        '''
        if self.next_opening > ts:
            return self.next_opening
        return 0

    def add_new_booking(self, ts, duration_sec):
        '''
        add new booking to the parking lot, extending next_opening
        @param ts: the starting time of the booking in unix epoch
        @param duration_sec: the duration of the booking in seconds
        '''
        # start off, remove all old bookings
        self.bookings = [x for x in self.bookings if x < int(time.time())]
        self.bookings.append(ts)
        self.next_opening = ts + duration_sec


class Garage(object):
    '''
    a collection of parking lots for booking.
    @param k_max_lot_number: maximum number of parking lots available

    Supported APIs are:
    get_parking_lot(duration_sec)
    '''

    def __init__(self, k_max_lot_number):
        '''creates k parking lots to begin with'''
        self.k_max_lot_number = k_max_lot_number
        self.pl_queue = PriorityQueue(maxsize=k_max_lot_number)
        for i in range(k_max_lot_number):
            self.pl_queue.put(ParkingLot(i + 1))

    def get_parking_lot(self, duration_sec):
        '''
        returns (lid, next_opening) for the first parking lot
        that has smallest next_opening. When parking is full, lid is -1
        '''
        candidate = self.pl_queue.get()     # thread-safe and blocking
        ts = int(time.time())               # get time after blocking call

        # non-critical section, before we put it back nobody's gonna touch it
        next_ts = candidate.get_next_opening(ts)
        final_ts = ts if next_ts == 0 else next_ts
        lid = candidate.lid if next_ts == 0 else -1

        if next_ts == 0:
            candidate.add_new_booking(final_ts, duration_sec)

        # re-insert and return
        self.pl_queue.put(candidate)
        return (lid, final_ts)

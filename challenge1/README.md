# garage

Garage is a parking lot manager.

To run the test, please do

```bash
python3.6 test.py
```

## Assumptions

* One garage singleton will be accessed by multiple threads concurrently, therefore garage is implemented with thread-safety in mind.

* When a parking lot is immediately available, the parking lot number is returned, while the parking lot data structure is modified to "remember" the booking. However, when no parking lot is immediately available, the earliest available time is returned with parking lot number -1. There will be no update on internal data structure.

* A vehicle may leave the parking lot earlier than its designated check-out time, but it may re-enter again as long as its assigned time window doesn't pass. Hence early-exit from a parking lot does not free-up the remaining time. This assumption was taken in order to simplify the problem and improve the speed of the algorithm, so as to avoid handling fragmented availability windows. However, if the purpose of the algorithm were to maximise the utility of the parking lots, then the Garage class can be modified to maintain two data structures -- a priority queue for parking lots whose availability time is integral/continuous, and a dictionary for parking lots whose availability time is scattered. Both data structures are thread-safe.

## Design Choices

### Python3.6

Garage is implemented in Python3.6.

2 major reaons motivated me choosing this version of Python:

* Python3 has more efficient GIL than Python2.7
* Python3 has builtin PriorityQueue data structure (to be explained later)

Among all sub-versions of Python3, 3.6 has the best documentation and active support.

### Garage Design

There are two classes defined by [garage.py](./garage.py).

* ParkingLot -- a simple object class maintains the bookings and the next available time
* Garage -- a class maintaining a fix-sized PriorityQueue of ParkingLots.

To find the best parking lot for an incoming request, the Garage sorts the ParkingLots based on their next availability time and parking lot number. ParkingLot with earlier availability will be ordered before those who are not immediately available. If two ParkingLots have the same availability window, then the ParkingLot with smaller number will be ordered in front. This ensures returning a vacant ParkingLot when the Garage is not full. In cases where the Garage is full, the earliest availability will be returned.

Internally, PriorityQueue is used to implement the sorting and re-order algorithm. The Python PriorityQueue class is implemented using heapq with locks. Seaching a ParkingLot takes `O(1)` while updating it takes `O(logN)`.

ParkingLot maintains a list of bookings by their starting timestamp. This is not necessary in the current setting -- one ParkingLot may receive maximum one booking. However, this design would easily extend to fullfill future bookings with little code change.

The order primitives (`__lt__()` etc.) are implemented to make the ParkingLot objects comparable.
# llc

Thank you for spending time reviewing the codes. Please find below a brief description of the file structure and run instructions.

## File Structure

|-|Challenge 1|Challenge 2|
|---|---|---|
|Source code|[garage.py](./challenge1/garage.py)|[socket_proxy.py](./challenge2/socket_proxy.py)|
|Unit test|[test.py](./challenge1/test.py)|[test.py](./challenge2/test.py)|
|Runnable|nil|[run.py](./challenge2/run.py)|
|Description|[README.md](./challenge1/README.md)|[README.md](./challenge2/README.md)|

Please check the corresponding README.md file for design choices and implementation details.

## Run Instructions

To test, please cd to the challange subdirectory and run

```bash
python3.6 test.py
```

To run challenge1, please wrap it in a directory (say $APP_ROOT/parking/) with a *__init__.py* file, and import via

```python
from parking.garage import Garage
```

To run challenge2, please make sure the receiving socket service is up and accessible from the testing machine, and then do:

```
python3.6 run.py -p <local_port> -i <remote_ip> -t <remote_port>
```

Then using any client of your choice. For example:

```bash
nc -v 127.0.0.1 <local_port>
```

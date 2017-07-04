# CityMatrixServer

This is the main UDP server that we have built to handle all of our city-related operations. We focus on two main server functions here: **ML** and **AI**.

1. **ML**: Run traffic and solar radiation linear regression analysis on a city to predict new values for the user.
2. **AI**: Given the current city state, *suggest* a new city that optimizes some weighted combination of metrics for the city.

## Setup

Before you begin the server for the first time, there are several steps you will need to complete.

1. Open `global/config.py` and be sure to verify all key settings for the server. The following variables are **especially** important.
	- `SERVER_OS` - Operating system of the prediction server, either MAC or WIN
	- `DEBUG` - Set to `False` if you are just playing around; `True` for production run
	- `INPUT_CITIES_DIRECTORY` - Directory to save incoming cities, before prediction
	- `PREDICTED_CITIES_DIRECTORY` - Directory to save outgoing cities, after prediction
	- `MODEL_DIR`, `LINEAR_MODEL_FILENAME` & `SOLAR_MODEL_FILENAME` - Important local relative paths to .pkl files that contain our sklearn estimator objects to run prediction

2. Run the setup script for the server with the following commands:

	```
	$ cd global
	$ python setup.py
	```

3. Now, the server should be ready to go. You can build the server directly from your text editor of choice, or run from command line:

	```
	$ cd CityMatrixServer
	$ python server.py
	```

The server should now begin waiting to receive new cities from the Grasshopper client.

## Common Problems

### 1. Port Collision Error

Sometimes, the UDP server runs into a port error, with a message that looks something like this:

```
...
socket.error: [Errno 48] Address already in use
...
```

There is a simple solution for this, depending on the operating system where you are running the server.

**For Windows users:**

1. Open Command Prompt by going to the Start menu and typing: `cmd`.
2. Run the following command:

	```
	FOR /F "tokens=4 delims= " %P IN ('netstat -a -n -o ^| findstr :7000') DO taskKill.exe /PID %P /F
	```

**For Mac OSX users:**

1. Open Terminal.
2. Run the following comand:

	```
	$ lsof -i :7000
	```
3. You will see an output like this:

	```
	COMMAND   PID  USER   FD   TYPE             DEVICE SIZE/OFF NODE
	Python  12345 Kevin   5u   IPv4 0xbb1b3b1a1b6ceb83      0t0  UDP
	```
4. The number in the `PID` column is the process ID of the Python server instance. Close the process with the following command:

	```
	$ sudo kill -9 <PID>
	```
	You may be required to enter your password to complete this operation.

<hr />

Once you complete these steps on your machine, you can restart the server.

### 2. Socket Message Length Error

Sometimes, the UDP server runs into a message length error, with a message that looks something like this:

```
...
socket.error: [Errno 40] Message too long
...
```

**For Mac OSX users:**

1. Open Terminal.
2. Run the following comand:

	```
	$ sudo sysctl -w net.inet.udp.maxdgram=65535
	```
	You may be required to enter your password to complete this operation.
	
<hr />

Once you complete these steps on your machine, you can restart the server.

## Current Configurations

Here are some current port configurations the server is using. *These are certainly subject to change.*

- 7000 - GH CV send to Python server
- 7001 - Python server send to Unity AI
- 7002 - Python server send to GH VIZ

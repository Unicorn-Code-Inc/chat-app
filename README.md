## chat-app
Chatting app I made (`Kwieeciol`) for when Teddy's in school.

## Installation
 1. First of all, download this repo with (you need [`git`](https://git-scm.com/)):
```
git clone https://github.com/Unicorn-Code-Inc/chat-app.git
```
 2. `cd` into the downloaded folder (`cd chat-app`)

 3. Install all the required libraries, can be done with:
```
pip install -r requirements.txt
```

## Setup
Open two terminal windows, `cd` into the project directory. 

In the first terminal type 
```py
python sender.py
```
this will be the window responsible for sending messages, this is where you type. To exit simply type `exit` and press `Enter`.

In the second window type
```py
python receiver.py
```
This will be the window responsible for receiving the actual messages, you **do not** type here. If you exit in the `sender` window, this should exit automatically.

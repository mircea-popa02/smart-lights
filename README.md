# Smart Lights
### Arduino UNO & WS2818b digital RGB strip

### Set up
Inside `app.py` change the name of USB device and port (*example*: `ser = serial.Serial('COM4', 9600)`) \ 
In the `.ino` project, change the port accordingly: `Serial.begin(9600);`

### Compiling the app
*Prerequisistes*: pyinstaller library (Windows) \
`pyinstaller --onefile --windowed --icon=images\icon.ico .\app.py`

![image](https://github.com/mircea-popa02/smart-lights/assets/59504943/07addfa4-28dc-4bac-a9dc-6b6ac8684be3)

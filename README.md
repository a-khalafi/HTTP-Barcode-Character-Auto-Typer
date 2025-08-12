# HTTP-Barcode-Character-Auto-Typer
A Python app that receives character strings (e.g., from mobile barcode scanner apps over HTTP), slices the numeric content, and auto-types it into any focused application using PyAutoGUI.

Features:
  1. Listens for barcode scans on a local web server
  2. Extracts digits using configurable slicing (e.g. `\[-5:]`, `\[:4]`)
  3. Types the digits using `pyautogui` into any open window
  4. System tray icon with change host, port, or slicing logic settings and safely shut down the app
     
Installation:
You can use standalone barcodescanner.exe or you can
  1. Install Python 3.8+ (from https://python.org)
  2. Clone this repository or download the files
  3. Install the required packages: (pip install -r requirements.txt)
  4. Run the app:(app.py)

Using with Android Barcode Scanner
  You can use any barcode scanner app that supports HTTP forwarding, such as Binary Eye.
  Setup Steps (Binary Eye):
  1. Install Binary Eye from the Play Store
  2. Go to Settings → Forward scans
  3. Enable Forward scans and Get mode and simply add content
  4. In URL to forward to , enter:
          
     example: http://192.168.1.100:5000/?content=
     
  Make sure your PC and phone are connected to the same Wi-Fi network
  
  Run the app on your PC (make sure about port and host)
  
  Scan a barcode using Binary Eye → the digits will be typed automatically
    
Settings:

Right-click the system tray icon to open Settings
<img width="257" height="171" alt="image" src="https://github.com/user-attachments/assets/1ef76981-af5c-47b1-907c-32cf3b4c7475" />

You can change:

  Host IP (default: 0.0.0.0)
  
  Port (default: 5000)
  
  Slice logic (default: \[:])
  
  Slice logic is applied to digits only. For example:
  
      [-5:] → last 5 digits
      
      [:4] → first 4 digits
      
      [2:6] → digits 3 to 6
  
Testing Without a Scanner:

With Browser:

  http://localhost:5000/?content=ABC123456
  
With curl:

  curl "http://localhost:5000/?content=ABC123456"


  

🙋‍♂️ Author: Amin Khalafi

amin_khalafi@yahoo.com

Hardware \& Embedded Systems Specialist

Reach out via GitHub or email if you'd like to collaborate!   

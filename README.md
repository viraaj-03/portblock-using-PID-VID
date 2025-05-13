# portblock-using-PID-VID
A simple Python GUI tool to safely eject USB devices using their Vendor ID (VID) and Product ID (PID).
🔌 USB Device Ejector

This is a Windows-only Python GUI tool that allows you to safely eject USB storage devices by specifying their **Vendor ID (VID)** and **Product ID (PID)**. It identifies the correct drive using WMI and performs a secure ejection using Windows system APIs.

---

📌 Features

- Easy-to-use GUI built with **Tkinter**
- Automatically matches **VID/PID** to the correct **drive letter**
- Ejects USB drives safely using `DeviceIoControl`
- Checks for **administrator privileges**
- Uses `pywin32` and `wmi` for system interaction

---

 🖥 Requirements

- Windows OS
- Python 3.x
- Admin privileges (required to perform ejection)

🧰 Dependencies

Install the required packages:

-bash
pip install pywin32 wmi


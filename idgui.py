import tkinter as tk
from tkinter import messagebox
import win32api
import win32con
import win32file
import ctypes
from ctypes import wintypes, Structure, POINTER, c_ulong, sizeof
from winioctlcon import FSCTL_LOCK_VOLUME, FSCTL_DISMOUNT_VOLUME, IOCTL_STORAGE_EJECT_MEDIA
import wmi
import re

# Structure definitions
class STORAGE_DEVICE_NUMBER(Structure):
    _fields_ = [
        ("DeviceType", wintypes.DWORD),
        ("DeviceNumber", wintypes.DWORD),
        ("PartitionNumber", wintypes.DWORD),
    ]

def is_admin():
    """Check if the script is running with administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception as e:
        print(f"Error checking for admin privileges: {e}")
        return False

def list_usb_devices():
    """List all removable drives."""
    drives = win32api.GetLogicalDriveStrings().split('\x00')[:-1]
    devices = []
    for drive in drives:
        if win32file.GetDriveType(drive) == win32con.DRIVE_REMOVABLE:
            devices.append(drive)
    return devices

def eject_drive(drive_letter):
    """Eject the specified drive."""
    try:
        handle = win32file.CreateFile(
            f"\\\\.\\{drive_letter.strip(':\\')}",
            win32file.GENERIC_READ | win32file.GENERIC_WRITE,
            win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE,
            None,
            win32con.OPEN_EXISTING,
            0,
            None,
        )

        win32file.DeviceIoControl(handle, FSCTL_LOCK_VOLUME, None, None)
        win32file.DeviceIoControl(handle, FSCTL_DISMOUNT_VOLUME, None, None)
        win32file.DeviceIoControl(handle, IOCTL_STORAGE_EJECT_MEDIA, None, None)
        win32file.CloseHandle(handle)
        messagebox.showinfo("Success", f"Drive {drive_letter} has been ejected.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to eject {drive_letter}: {e}")

def find_drive_by_vid_pid(target_vid, target_pid):
    """Find the drive letter by matching VID and PID."""
    try:
        c = wmi.WMI()
        for usb in c.Win32_DiskDrive():
            if "USB" in usb.InterfaceType:
                match = re.search(r"VID_([0-9A-F]+)&PID_([0-9A-F]+)", usb.PNPDeviceID, re.I)
                if match:
                    vid = int(match.group(1), 16)
                    pid = int(match.group(2), 16)
                    if vid == target_vid and pid == target_pid:
                        for partition in usb.associators("Win32_DiskDriveToDiskPartition"):
                            for logical in partition.associators("Win32_LogicalDiskToPartition"):
                                return logical.DeviceID + "\\"
    except Exception as e:
        print(f"Error in WMI device search: {e}")
    return None

def eject_device_by_vid_pid(vid, pid):
    """Eject a USB device by VID and PID."""
    drive = find_drive_by_vid_pid(vid, pid)
    if drive:
        eject_drive(drive)
    else:
        messagebox.showerror("Error", "No matching USB device found with the given VID and PID.")

def main():
    if not is_admin():
        messagebox.showerror("Error", "This script requires administrator privileges.")
        return

    root = tk.Tk()
    root.title("USB Device Ejector")

    def on_eject_click():
        try:
            vid = int(vid_entry.get(), 16)
            pid = int(pid_entry.get(), 16)
            eject_device_by_vid_pid(vid, pid)
        except ValueError:
            messagebox.showerror("Error", "Please enter valid hexadecimal VID and PID.")

    tk.Label(root, text="VID (Hex):").grid(row=0, column=0, padx=10, pady=5)
    vid_entry = tk.Entry(root, width=10)
    vid_entry.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(root, text="PID (Hex):").grid(row=1, column=0, padx=10, pady=5)
    pid_entry = tk.Entry(root, width=10)
    pid_entry.grid(row=1, column=1, padx=10, pady=5)

    tk.Button(root, text="Eject Device", command=on_eject_click).grid(row=2, column=0, columnspan=2, pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()

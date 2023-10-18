# This was done in a haste and improvements can be made. Make a pull request if you want to contribute. Any help is appreciated.



### Libraries ###
import win10toast as W10T
import tinytuya as TUYA
import linecache as LNC
import subprocess as SP
import keyboard as KB
import datetime as DT
import psutil as PSU
import sys as System
import json as JSON
import time as Task
import ctypes as CT
import os as OS



### Presentation ###
print('  __  __     __     __     ______     ______     ______    __         ______     ______    ______     ______ \n /\ \/\ \   /\ \   /\ \   /\  __ \   /\  ___\   /\  <> \  /\ \       /\  ___\   /\__  _\  /\  ___\   /\  <> \ \n \ \ \_\ \  \ \ \  \ \ \  \ \ \_\ \  \ \  __\   \ \  _ /  \ \ \____  \ \  __\   \/_/\ \/  \ \  __\   \ \  _ <_\n  \ \_____\  \ \_\  \ \_\  \ \____/   \ \_____\  \ \_\/    \ \_____\  \ \_____\    \ \_\   \ \_____\  \ \_\ \_\ \n   \______/   \__/   \/_/   \_____/    \______/   \__/      \______/   \______/     \__/    \______/   \__/\/_/ \n \n Press Shift + S at any time to change your settings. \n Press Alt + S at any time to see your statistics. \n\n\n')



### Variables ###
class FLASHWINFO(CT.Structure):
    _fields_ = [
        ("cbSize", CT.c_uint),
        ("hwnd", CT.c_void_p),
        ("dwFlags", CT.c_uint),
        ("uCount", CT.c_uint),
        ("dwTimeout", CT.c_uint)
    ]

finfo = FLASHWINFO()
finfo.cbSize = CT.sizeof(finfo)
finfo.hwnd = CT.windll.kernel32.GetConsoleWindow()
finfo.dwFlags = 2
finfo.uCount = 0
finfo.dwTimeout = 0

Notifier = W10T.ToastNotifier()

MinLevel = 25
MaxLevel = 75

CheckFrequency = 60
ThreadSlept = CheckFrequency

Notify = True
Flash = True

InputMode = False

Type = 'None'
LastType = 'None'

Timestamp = 'None'
TimestampText = 'None'

OutletID = 'None'
OutletIP = 'None'
OutletLocalKey = 'None'

TimesPlugged = 0
TimesUnplugged = 0
TimesStable = 0



### Functions ###
def NotifyError():
    global Notify, Flash

    try:
        if Notify:
            Notifier.show_toast("uNdepleter", "An error has occured", duration = 3)
        
        if Flash:
            CT.windll.user32.FlashWindowEx(CT.byref(finfo))

    except Exception as Err:
        CacheError(Err, '[I] Unexpected error')

def ConsoleLog(TextType: str, Text: str, Safeguard: bool = False):
    global TimestampText, Timestamp, LastType, Type

    try:
        Type = TextType.strip()

        if LastType != 'None':
            if Type != LastType:
                if (
                    LastType != 'ERROR' and
                    LastType != 'LOW' and
                    LastType != 'STABLE' and
                    LastType != 'HIGH'
                ):
                    print('\n')  
            
                elif (
                    LastType == 'LOW' or
                    LastType == 'STABLE' or
                    LastType == 'HIGH') and (
                        Type != 'LOW' or
                        Type != 'STABLE' or
                        Type != 'HIGH'
                ):
                    print('\n')

                elif LastType == 'ERROR':
                    if Type != 'CACHE':
                        print('\n')

        if Type == 'ERROR':
            NotifyError()

        print(f' {TextType} | {Timestamp} | {Text}')
        LastType = Type

    except Exception as Err:
        NotifyError()
        
        if Safeguard:
            try:
                exc_type, exc_obj, tb = System.exc_info()
                f = tb.tb_frame

                LineNumber = tb.tb_lineno
                FileName = f.f_code.co_filename
                FunctionName = f.f_code.co_name
                ErrorMessage = str(exc_obj)

                LNC.checkcache(FileName)
                Line = LNC.getline(FileName, LineNumber, f.f_globals).strip()
    
            except Exception as InErr:
                FileName, FunctionName, LineNumber, Line, ErrorMessage = 'Unknown', 'Unknown', 'Unknown', 'Unknown', 'Unknown'
    
                print(f'ERROR  | {Timestamp} | Unable to retrieve complete error information - please contact support with the following information: \n {FileName}, \n {str(FunctionName)}, \n {str(LineNumber)}, \n {str(Line)} \n {str(InErr)}, \n {str(ErrorMessage)}, \n {str(type(InErr))}, \n {repr(InErr)}, \n {str(InErr.__context__)}, \n {str(InErr.__traceback__)}, \n {str(InErr.__cause__)}, \n {str(InErr.args)}')

            print(f'ERROR  | {Timestamp} | Unable to log to console - please contact support with the following information: \n {FileName}, \n {str(FunctionName)}, \n {str(LineNumber)}, \n {str(Line)} \n {str(Err)}, \n {str(ErrorMessage)}, \n {str(type(Err))}, \n {repr(Err)}, \n {str(Err.__context__)}, \n {str(Err.__traceback__)}, \n {str(Err.__cause__)}, \n {str(Err.args)}')

        else:
            CacheError(Err, '[II] Unexpected error')

def CreateCache(File: str, Folder: str, Data: {}):
    FolderPath = f'Cache\\{Folder}'
    Path = f'{FolderPath}\\{File}.json'

    try:
        OS.makedirs('Cache', exist_ok = True)
        OS.makedirs(FolderPath, exist_ok = True)

        i = 0
        with open(Path, 'w') as CacheFile:
            if Folder == 'Errors':
                for Key, Item in Data.items():
                    if i != 0:
                        CacheFile.write('\n')

                    JSON.dump({str(Key): str(Item)}, CacheFile) 
                    i += 1
            
                ConsoleLog('CACHE ', f'Successfully logged error at {Path}!') 

            elif Folder == 'Settings':
                JSON.dump(Data, CacheFile)

                if not File == 'Statistics':
                    ConsoleLog('CACHE ', f'Successfully saved {File.lower()} at {Path}!') 
        
        return list(Data.values())

    except FileNotFoundError:
        pass
        
    except (JSON.JSONDecodeError, OSError, IOError):
        ConsoleLog('ERROR ', f'Couldn\'t create such file or directory - \'\\{Path}\'.')

    except Exception as Err:
        CacheError(Err, 'cache data', True)

def ReadCache(File: str, Folder: str, Defaults: {}):
    Path = f'Cache\\{Folder}\\{File}.json'
    
    try:
        with open(Path, 'r') as CacheFile:
            Data = JSON.load(CacheFile)

        return Data

    except FileNotFoundError:
        pass

    except JSON.JSONDecodeError:
        ConsoleLog('ERROR ', f'Couldn\'t read such file or directory - \'\\{Path}\'.')

    except Exception as Err:
        CacheError(Err, f'[III] Unexpected error')

    return Defaults

def CacheError(Err: Exception, Message: str, Safeguard: bool = False):
    try:
        exc_type, exc_obj, tb = System.exc_info()
        f = tb.tb_frame

        LineNumber = tb.tb_lineno
        FileName = f.f_code.co_filename
        FunctionName = f.f_code.co_name
        ErrorMessage = str(exc_obj)

        LNC.checkcache(FileName)
        Line = LNC.getline(FileName, LineNumber, f.f_globals).strip()
    
    except Exception as Err:
        FileName, FunctionName, LineNumber, Line, ErrorMessage = 'Unknown', 'Unknown', 'Unknown', 'Unknown', 'Unknown'

        if Safeguard:
            ConsoleLog('ERROR ', f'Unable to {Message} - please contact support with the following information: \n {FileName}, \n {str(FunctionName)}, \n {str(LineNumber)}, \n {str(Line)} \n {str(Err)}, \n {str(ErrorMessage)}, \n {str(type(Err))}, \n {repr(Err)}, \n {str(Err.__context__)}, \n {str(Err.__traceback__)}, \n {str(Err.__cause__)}, \n {str(Err.args)}', True)

        else:
            ConsoleLog('ERROR ', f'{Message} - {str(Err)}.', True)
            CreateCache(f'Thrown@{TimestampText}', 'Errors', {
                'FileName': FileName,
                'FunctionCall': FunctionName,
                'LineNumber': LineNumber,
                'Line': Line,
                'Error': Err,
                'Message': ErrorMessage,
                'Type': type(Err),
                'Explanation': repr(Err),
                'Context': Err.__context__,
                'Traceback': Err.__traceback__,
                'Cause': Err.__cause__,
                'Arguments': Err.args,
            })
        
    if Safeguard:
        ConsoleLog('ERROR ', f'Unable to {Message} - please contact support with the following information: \n {FileName}, \n {str(FunctionName)}, \n {str(LineNumber)}, \n {str(Line)} \n {str(Err)}, \n {str(ErrorMessage)}, \n {str(type(Err))}, \n {repr(Err)}, \n {str(Err.__context__)}, \n {str(Err.__traceback__)}, \n {str(Err.__cause__)}, \n {str(Err.args)}', True)

    else:
        ConsoleLog('ERROR ', f'{Message} - {str(Err)}.', True)
        CreateCache(f'Thrown@{TimestampText}', 'Errors', {
            'FileName': FileName,
            'FunctionCall': FunctionName,
            'LineNumber': LineNumber,
            'Line': Line,
            'Error': Err,
            'Message': ErrorMessage,
            'Type': type(Err),
            'Explanation': repr(Err),
            'Context': Err.__context__,
            'Traceback': Err.__traceback__,
            'Cause': Err.__cause__,
            'Arguments': Err.args,
        })

def RunAsynchronously(Command: str):
    global TimestampText, Timestamp

    try:
        Process = SP.Popen(f'start "" "{Command}"', shell = True)
        Process.communicate()

    except FileNotFoundError:
        pass

    except OSError:
        ConsoleLog('ERROR ', f'Couldn\'t find such file or directory - \'\\{Command}\'.')
    
    except SP.TimeoutExpired:
        ConsoleLog('ERROR ', 'Timeout expired.')
    
    except Exception as Err:
        CacheError(Err, '[IV] Unexpected error')

def RetrieveBattery():
    global TimestampText, Timestamp

    try:
        Battery = PSU.sensors_battery()
        
        if Battery is None:
            ConsoleLog('ERROR ', 'No battery was found within the current system\'s hardware.')

        else:
            Plugged = Battery.power_plugged
            Percent = Battery.percent
    
            return Percent, Plugged

    except Exception as Err:
        CacheError(Err, '[V] Unexpected error')

def RetrieveTime():
    try:
        return DT.datetime.now().strftime('%m/%d, %H:%M:%S.%f')[:-3]
    
    except Exception as Err:
        CacheError(Err, '[VI] Unexpected error')

        return 'UNKNOWN'

def RetrieveStatistics(Action: str, Times: int):
    if Times < 0:
        ConsoleLog('INFO  ', f'Bro, why even bother hacking this...? Was {Action} {Times} times, if you still want to know.')
    
    elif Times == 0:
        ConsoleLog('INFO  ', f'Your PC has not yet been {Action} [by uNdepleter].')

    elif Times == 1:
        ConsoleLog('INFO  ', f'Your PC was {Action} [by uNdepleter] {Times} time.')

    elif Times > 1:
        ConsoleLog('INFO  ', f'Your PC was {Action} [by uNdepleter] {Times} times.')



### Functionality ###
Data = ReadCache('Configuration', 'Settings', {
    'BatteryCheckFrequency': CheckFrequency,
    'MinimumBatteryLevel': MinLevel,
    'MaximumBatteryLevel': MaxLevel,
    'NotifyingAllowed': Notify,
    'FlashingAllowed': Flash,
})
ThreadSlept = int(Data['BatteryCheckFrequency'])

while True:
    try:
        Data = ReadCache('Credentials', 'Settings', {
            'OutletID': OutletID,
            'OutletIP': OutletIP,
            'OutletLocalKey': OutletLocalKey,
        })
        OutletID, OutletIP, OutletLocalKey = str(Data['OutletID']), str(Data['OutletIP']), str(Data['OutletLocalKey'])

        Data = ReadCache('Statistics', 'Settings', {
            'Stable': TimesStable,
            'Plugged': TimesPlugged,
            'Unplugged': TimesUnplugged,
        })
        TimesStable, TimesPlugged, TimesUnplugged = int(Data['Stable']), int(Data['Plugged']), int(Data['Unplugged'])

        Data = ReadCache('Configuration', 'Settings', {
            'BatteryCheckFrequency': CheckFrequency,
            'MinimumBatteryLevel': MinLevel,
            'MaximumBatteryLevel': MaxLevel,
            'NotifyingAllowed': Notify,
            'FlashingAllowed': Flash,
        })
        CheckFrequency, MinLevel, MaxLevel, Notify, Flash = int(Data['BatteryCheckFrequency']), int(Data['MinimumBatteryLevel']), int(Data['MaximumBatteryLevel']), bool(Data['NotifyingAllowed']), bool(Data['FlashingAllowed'])

        Percent, Plugged = RetrieveBattery()

        PercentText = str(Percent)
        PluggedText = Plugged and 'plugged-in' or 'not plugged-in' 

        Timestamp = RetrieveTime()
        TimestampText = Timestamp.replace(':', '.')

        if OutletID == 'None' or OutletIP == 'None' or OutletLocalKey == 'None':
            if ThreadSlept >= CheckFrequency:
                ConsoleLog('ERROR ', 'Couldn\'t find any Smart Outlet\'s credentials.')
                ConsoleLog('INFO  ', 'Forcing into Input Mode.')
                ConsoleLog('INFO  ', 'Opening a input terminal.')
                RunAsynchronously('Input Mode.py')

                ThreadSlept = 0

        else:
            Outlet = TUYA.OutletDevice(OutletID, OutletIP, OutletLocalKey)
            Outlet.set_version(3.3)

            if KB.is_pressed('shift+s'):
                InputMode = not InputMode
        
                if InputMode:
                    ConsoleLog('INFO  ', 'You just entered Input Mode!')
                    ConsoleLog('INFO  ', 'Press C to change your settings.')
                    ConsoleLog('INFO  ', 'Press Shift + S again to exit.')

                else:
                    ConsoleLog('INFO  ', 'Exited Input Mode.')
            
            elif KB.is_pressed('alt+s'):
                RetrieveStatistics('checked as battery-stable', TimesStable)
                RetrieveStatistics('plugged', TimesPlugged)
                RetrieveStatistics('unplugged', TimesUnplugged)
                
            elif KB.is_pressed('c') and InputMode:
                InputMode = False

                ConsoleLog('INFO  ', 'Opening a input terminal.')
                RunAsynchronously('Input Mode.py')
                ConsoleLog('INFO  ', 'Automatically left Input Mode.')

            if ThreadSlept >= CheckFrequency:  
                if Percent > MinLevel and Percent < MaxLevel:        
                    ConsoleLog('STABLE', f'Your battery is currently at {PercentText}% and {PluggedText}. Nothing will be done.')

                    TimesStable += 1
                    
                elif Percent <= MinLevel and not Plugged:  
                    ConsoleLog('LOW   ', f'Your battery is currently at {PercentText}% and {PluggedText}. Plugging now.')
                    Outlet.turn_on()
    
                    TimesPlugged += 1

                elif Percent >= MaxLevel and Plugged:  
                    ConsoleLog('HIGH  ', f'Your battery is currently at {PercentText}% and {PluggedText}. Unplugging now.')
                    Outlet.turn_off()

                    TimesUnplugged += 1 

                CreateCache('Statistics', 'Settings', {
                    'Stable': TimesStable,
                    'Plugged': TimesPlugged,
                    'Unplugged': TimesUnplugged,
                })

                if InputMode:
                    ConsoleLog('INFO  ', 'You are still in Input Mode!')
                    ConsoleLog('INFO  ', 'Press C to change your settings.')
                    ConsoleLog('INFO  ', 'Press Shift + S to exit.')

                ThreadSlept = 0

    except Exception as Err:
        CacheError(Err, '[VIII] Unexpected error')

    ThreadSlept += 0.3
    Task.sleep(0.3)

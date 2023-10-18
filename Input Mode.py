# This was done in a haste and improvements can be made. Make a pull request if you want to contribute.



### Imports ###
import win10toast as W10T
import linecache as LNC
import subprocess as SP
import datetime as DT
import sys as System
import ctypes as CT
import json as JSON
import os as OS



### Presentation ###
print('  __  __     __     __     ______     ______     ______    __         ______     ______    ______     ______ \n /\ \/\ \   /\ \   /\ \   /\  __ \   /\  ___\   /\  <> \  /\ \       /\  ___\   /\__  _\  /\  ___\   /\  <> \ \n \ \ \_\ \  \ \ \  \ \ \  \ \ \_\ \  \ \  __\   \ \  _ /  \ \ \____  \ \  __\   \/_/\ \/  \ \  __\   \ \  _ <_\n  \ \_____\  \ \_\  \ \_\  \ \____/   \ \_____\  \ \_\/    \ \_____\  \ \_____\    \ \_\   \ \_____\  \ \_\ \_\ \n   \______/   \__/   \/_/   \_____/    \______/   \__/      \______/   \______/     \__/    \______/   \__/\/_/ \n \n Changing your settings. An empty value makes the setting remain unchanged. \n Close this window to cancel all changes. \n\n\n')



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

DefaultCredentials = 'None'

DefaultNotify = True
DefaultFlash = True

DefaultCheckFrequency = 60
DefaultMinLevel = 20
DefaultMaxLevel = 80

CredentialsMessage = 'What is your TUYA\'s Smart Outlet\'s'
NotificationMessage = 'Should the APP be allowed to'
LevelMessage = 'Which battery level should trigger the Smart Outlet'

Type = 'None'
LastType = 'None'

Timestamp = 'None'
TimestampText = 'None'



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

def RetrieveUserInput(Message: str, Value: int, DefaultValue: int):
    global LastType

    try:
        LastType = 'INPUT'
        UserInput = input(f'''
 INPUT | {Timestamp} | {Message}?
 INPUT | {Timestamp} | (default => {str(DefaultValue)}; actual => {str(Value)}): ''')
        
        return UserInput if UserInput != '' else Value
    
    except Exception as Err:
        CacheError(Err, '[IV] Unexpected error')

        return 'Error whilst processing user input'
    
def RetrieveTime():
    try:
        return DT.datetime.now().strftime('%m/%d, %H:%M:%S.%f')[:-3]
    
    except Exception as Err:
        CacheError(Err, '[V] Unexpected error')

        return 'UNKNOWN'



### Functionality ###
try:
    Timestamp = RetrieveTime()
    TimestampText = Timestamp.replace(':', '.')

    Data = ReadCache('Credentials', 'Settings', {
        'OutletID': DefaultCredentials,
        'OutletIP': DefaultCredentials,
        'OutletLocalKey': DefaultCredentials,
    })
    OutletID, OutletIP, OutletLocalKey = str(Data['OutletID']), str(Data['OutletIP']), str(Data['OutletLocalKey'])

    Data = ReadCache('Configuration', 'Settings', {
        'BatteryCheckFrequency': DefaultCheckFrequency,
        'MinimumBatteryLevel': DefaultMinLevel,
        'MaximumBatteryLevel': DefaultMaxLevel,
        'NotifyingAllowed': DefaultNotify,
        'FlashingAllowed': DefaultFlash,
    })
    CheckFrequency, MinLevel, MaxLevel, Notify, Flash = int(Data['BatteryCheckFrequency']), int(Data['MinimumBatteryLevel']), int(Data['MaximumBatteryLevel']), bool(Data['NotifyingAllowed']), bool(Data['FlashingAllowed'])

    OutletID = RetrieveUserInput(f'{CredentialsMessage} ID', OutletID, DefaultCredentials)
    OutletIP = RetrieveUserInput(f'{CredentialsMessage} IP', OutletIP, DefaultCredentials)
    OutletLocalKey = RetrieveUserInput(f'{CredentialsMessage} Local Key', OutletLocalKey, DefaultCredentials)

    CheckFrequency = RetrieveUserInput('How often should the battery checks occur (in seconds)', CheckFrequency, DefaultCheckFrequency)
    MinLevel = RetrieveUserInput(f'{LevelMessage} on', MinLevel, DefaultMinLevel)
    MaxLevel = RetrieveUserInput(f'{LevelMessage} off', MaxLevel, DefaultMaxLevel)
    Notify = RetrieveUserInput(f'{NotificationMessage} send taskbar notifications (y/n)', Notify, DefaultNotify)
    Flash = RetrieveUserInput(f'{NotificationMessage} flash the taskbar (y/n)', Flash, DefaultFlash)

    CreateCache('Credentials', 'Settings', {
        'OutletID': OutletID,
        'OutletIP': OutletIP,
        'OutletLocalKey': OutletLocalKey,
    })

    CreateCache('Configuration', 'Settings', {
        'BatteryCheckFrequency': CheckFrequency,
        'MinimumBatteryLevel': MinLevel,
        'MaximumBatteryLevel': MaxLevel,
        'NotifyingAllowed': Notify,
        'FlashingAllowed': Flash,
    })

    ConsoleLog('INFO ', 'Done! You can now close this terminal.')
    print('\n\n\n')

except Exception as Err:
    CacheError(Err, '[VI] Unexpected error')

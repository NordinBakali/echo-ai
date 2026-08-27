Option Explicit

Dim fso, shell, scriptDir, launcherPath
Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")

scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
launcherPath = fso.BuildPath(scriptDir, "Start-Echo-WakeListener.bat")

If Not fso.FileExists(launcherPath) Then
    MsgBox "Start-Echo-WakeListener.bat not found in: " & scriptDir, vbCritical, "Echo Wake Listener Error"
    WScript.Quit 1
End If

shell.Run Chr(34) & launcherPath & Chr(34), 0, False

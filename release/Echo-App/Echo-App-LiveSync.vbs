Option Explicit

Dim fso, shell, scriptDir, launcherPath
Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")

scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
launcherPath = fso.BuildPath(scriptDir, "Start-Echo-App-LiveSync.bat")

If Not fso.FileExists(launcherPath) Then
    MsgBox "Start-Echo-App-LiveSync.bat not found in: " & scriptDir, vbCritical, "Echo Live Sync Launcher Error"
    WScript.Quit 1
End If

shell.Run Chr(34) & launcherPath & Chr(34), 0, False

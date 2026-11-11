Option Explicit
Dim shell, files, folder, python, entry
Set shell = CreateObject("WScript.Shell")
Set files = CreateObject("Scripting.FileSystemObject")
folder = files.GetParentFolderName(WScript.ScriptFullName)
python = files.BuildPath(folder, "venv\Scripts\pythonw.exe")
entry = files.BuildPath(folder, "desktop.py")
If Not files.FileExists(python) Then
    MsgBox "Instale o ambiente e as dependencias desktop conforme o README.pt-br.md antes de abrir.", vbExclamation, "YouTube Converter"
    WScript.Quit 1
End If
shell.CurrentDirectory = folder
shell.Run Chr(34) & python & Chr(34) & " " & Chr(34) & entry & Chr(34), 0, False

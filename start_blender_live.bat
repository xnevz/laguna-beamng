@echo off
echo Starting Blender 5.3 with Renault Laguna Master Project & AI Live Bridge...
start "" "C:\Program Files\Blender Foundation\Blender 5.3\blender.exe" "%~dp0blender\laguna_master.blend" --python "%~dp0tools\blender_bridge_server.py"
echo Blender launched! The bridge server is listening on port 9876.
pause

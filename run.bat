@echo off

IF NOT DEFINED VIRTUAL_ENV (
    call attendance-venv\Scripts\activate
)

python -m app.main
pause
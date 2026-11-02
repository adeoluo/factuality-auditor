# Records docs/demo/audit.gif from a real run: `vhs docs/demo/audit.tape` from the repo root.
Output docs/demo/audit.gif
Set Shell "bash"
Set FontSize 15
Set Width 1300
Set Height 480
Set Padding 18
Set Theme "Catppuccin Mocha"
Set TypingSpeed 22ms

Hide
Type `export PS1='$ ' && uv sync -q && source .venv/bin/activate && clear` Enter
Sleep 10s
Show
Type `python -m factuality_auditor audit "Mars has 5 moons."` Enter
Sleep 2.5s
Type `python -m factuality_auditor evaluate` Enter
Sleep 3s

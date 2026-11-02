# Records docs/demo/audit-more.gif from a real run: `vhs docs/demo/audit-more.tape` from the repo root.
Output docs/demo/audit-more.gif
Set Shell "bash"
Set FontSize 15
Set Width 1300
Set Height 440
Set Padding 18
Set Theme "Catppuccin Mocha"
Set TypingSpeed 22ms

Hide
Type `export PS1='$ ' && uv sync -q && source .venv/bin/activate` Enter
Sleep 2s
Sleep 10s
Type `clear` Enter
Sleep 1s
Show
Type `python -m factuality_auditor audit "Mars has 2 moons."` Enter
Sleep 2.5s
Type `python -m factuality_auditor audit "The Eiffel Tower is in Berlin."` Enter
Sleep 3s

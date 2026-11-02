# Records docs/demo/demonstrate.gif from a real run: `vhs docs/demo/demonstrate.tape` from the repo root.
Output docs/demo/demonstrate.gif
Set Shell "bash"
Set FontSize 15
Set Width 1300
Set Height 620
Set Padding 18
Set Theme "Catppuccin Mocha"
Set TypingSpeed 25ms

Hide
Type "export PS1='$ ' && uv sync -q && source .venv/bin/activate && clear" Enter
Sleep 4s
Show
Type "python -m react_agent demonstrate" Enter
Sleep 5s

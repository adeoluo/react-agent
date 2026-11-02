# Records docs/demo/http.gif from a real run: `vhs docs/demo/http.tape` from the repo root.
Output docs/demo/http.gif
Set Shell "bash"
Set FontSize 15
Set Width 1300
Set Height 620
Set Padding 18
Set Theme "Catppuccin Mocha"
Set TypingSpeed 22ms

Hide
Type `export PS1='$ ' && uv sync -q && source .venv/bin/activate` Enter
Sleep 2s
Type `python -m react_agent serve --port 18323 >/dev/null 2>&1 &` Enter
Sleep 2s
Sleep 8.0s
Type `clear` Enter
Sleep 1s
Show
Type `curl -s localhost:18323/health; echo` Enter
Sleep 1.5s
Type `curl -s localhost:18323/run -d '{"question": "What is the capital of Japan?", "max_steps": 4}' | jq` Enter
Sleep 4s
Hide
Type `kill %1` Enter
Sleep 1s

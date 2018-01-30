# run-on-idle
A small tool to run programs when computer is idle, to run intensive computation, synchronisation, crypto mining, whatever you want.

## tldr
install xprintidle
```
cp config.json.tpl config.json
python3 ./run_on_idle.py
```

## config file:
see the config.json.tpl that should be clear enough:

`trigger_cmd`: the command that will start the idle program
`kill_cmd`: the command that will stop the idle program
`delay_processes`: list of processes that should prevent idle program execution (ex mplayer if you don't want to destroy your film)

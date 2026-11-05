"""Talk to the agent in your terminal, as if you were phoning the gym.

    uv run python -m gym_agent.chat                 # call as Dana (a parent, not a member)
    uv run python -m gym_agent.chat --caller priya  # call as a family member
    uv run python -m gym_agent.chat --prompt-label staging
    uv run python -m gym_agent.chat --prompt-file ../prompts/system_v1.md

While chatting:
    /good, /bad <why>   score the last turn in Langfuse (this is how real traces become test cases)
    /trace              print the Langfuse link for the last turn
    /end                hang up (writes long-term memories), then exit
"""

from __future__ import annotations

import argparse
from pathlib import Path

from langfuse import get_client
from rich.console import Console
from rich.panel import Panel

from .agent import GymAgent
from .config import langfuse_enabled
from .gym import load_callers

console = Console()


def main() -> None:
    p = argparse.ArgumentParser(prog="python -m gym_agent.chat")
    p.add_argument("--caller", default="dana", choices=sorted(load_callers()))
    p.add_argument("--prompt-label", default=None, help="Langfuse prompt label (default: production)")
    p.add_argument("--prompt-file", type=Path, default=None, help="use a local prompt file instead of Langfuse")
    p.add_argument("--message", "-m", action="append", help="send these messages and exit (non-interactive)")
    args = p.parse_args()

    agent = GymAgent.from_env(prompt_label=args.prompt_label, prompt_file=args.prompt_file)
    call = agent.start_call(args.caller)
    lf = get_client()
    console.print(Panel.fit(
        f"[bold]Ridgeline Climbing Gym[/] phone line  |  caller: [cyan]{args.caller}[/]  |  "
        f"prompt: {agent.prompt.version}  |  tools: {', '.join(agent.tools) or 'none'}  |  "
        f"memory: {'on' if agent.handbook else 'off'}  |  tracing: {'on' if langfuse_enabled() else 'off'}",
        title="gym_agent.chat"))

    last = None
    queue = list(args.message or [])
    while True:
        text = queue.pop(0) if queue else (None if args.message else console.input("[bold blue]caller>[/] ").strip())
        if text is None or text in ("/end", "/quit", "/exit"):
            break
        if not text:
            continue
        if text.startswith(("/good", "/bad")):
            if last and last.trace_id and langfuse_enabled():
                good = text.startswith("/good")
                comment = text.partition(" ")[2] or None
                lf.create_score(trace_id=last.trace_id, name="user_feedback", value=1 if good else 0,
                                data_type="BOOLEAN", comment=comment)
                console.print(f"[dim]scored the last turn {'good' if good else 'bad'} in Langfuse[/]")
            else:
                console.print("[dim]nothing to score (is Langfuse set up? see Lab 2)[/]")
            continue
        if text == "/trace":
            url = lf.get_trace_url(trace_id=last.trace_id) if last and last.trace_id else None
            console.print(url or "[dim]no trace yet (is Langfuse set up? see Lab 2)[/]")
            continue

        if args.message:
            console.print(f"[bold blue]caller>[/] {text}")
        last = call.send(text)
        for tc in last.tool_calls:
            console.print(f"  [orange3]tool[/] {tc['name']}({tc['arguments']}) -> {str(tc['result'])[:140]}")
        console.print(f"[bold magenta]agent>[/] {last.reply}\n")

    facts = call.end()
    if facts:
        console.print("[teal]remembered:[/] " + "; ".join(facts))
    lf.flush()  # send any buffered traces before the process exits
    console.print(f"[dim]call {call.call_id} ended.[/]")


if __name__ == "__main__":
    main()

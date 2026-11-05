from __future__ import annotations


def make_agent(llm, **kwargs):
    from gym_agent.agent import GymAgent
    from gym_agent.gym import BookingStore
    from gym_agent.prompts import SystemPrompt

    kwargs.setdefault("tools", [])
    kwargs.setdefault("prompt", SystemPrompt(text="You are Ridgeline's phone assistant.", version="test"))
    kwargs.setdefault("bookings", BookingStore.in_memory())
    return GymAgent(llm, **kwargs)


def system_message(request: dict) -> str:
    return request["messages"][0]["content"]

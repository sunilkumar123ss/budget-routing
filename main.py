"""Deterministic offline routing based on configured capacities and budgets."""
import argparse
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path
import sys


def amount(value):
    try:
        result = Decimal(str(value))
    except InvalidOperation as error:
        raise ValueError("invalid money value") from error
    if not result.is_finite() or result < 0:
        raise ValueError("money values must be finite and nonnegative")
    return result


def integer(value, name, minimum=0):
    if type(value) is not int or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")
    return value


def route(models, requests, budget):
    if not isinstance(models, list) or not models or not isinstance(requests, list):
        raise ValueError("models must be a nonempty list and requests a list")
    names = set()
    for model in models:
        if not isinstance(model["name"], str) or not model["name"] or model["name"] in names:
            raise ValueError("model names must be unique nonempty strings")
        names.add(model["name"])
        integer(model["context_tokens"], "context_tokens", 1)
        integer(model["estimated_latency_ms"], "estimated_latency_ms")
        if not isinstance(model["capabilities"], list) or any(not isinstance(x, str) for x in model["capabilities"]):
            raise ValueError("capabilities must be string lists")
        amount(model["input_price_per_million"])
        amount(model["output_price_per_million"])
    remaining, outputs, seen = amount(budget), [], set()
    for request in requests:
        if not isinstance(request["id"], str) or not request["id"] or request["id"] in seen:
            raise ValueError("request IDs must be unique nonempty strings")
        seen.add(request["id"])
        input_tokens = integer(request["input_tokens"], "input_tokens")
        output_tokens = integer(request["max_output_tokens"], "max_output_tokens")
        latency = integer(request["max_latency_ms"], "max_latency_ms")
        ceiling = amount(request["max_cost"])
        if not isinstance(request["required_capabilities"], list) or any(not isinstance(x, str) for x in request["required_capabilities"]):
            raise ValueError("required_capabilities must be a string list")
        candidates, excluded = [], {}
        for model in models:
            reasons = []
            cost = (input_tokens * amount(model["input_price_per_million"]) +
                    output_tokens * amount(model["output_price_per_million"])) / 1_000_000
            if input_tokens + output_tokens > model["context_tokens"]:
                reasons.append("context_capacity")
            if not set(request["required_capabilities"]).issubset(model["capabilities"]):
                reasons.append("capabilities")
            if model["estimated_latency_ms"] > latency:
                reasons.append("configured_latency")
            if cost > ceiling:
                reasons.append("request_budget")
            if cost > remaining:
                reasons.append("remaining_batch_budget")
            if reasons:
                excluded[model["name"]] = reasons
            else:
                candidates.append((cost, model["estimated_latency_ms"], model["name"]))
        if candidates:
            cost, _, name = min(candidates)
            remaining -= cost
            outputs.append({"id": request["id"], "status": "routed", "model": name, "reserved_cost": str(cost)})
        else:
            outputs.append({"id": request["id"], "status": "rejected", "excluded_models": excluded})
    return {"decisions": outputs, "remaining_budget": str(remaining)}


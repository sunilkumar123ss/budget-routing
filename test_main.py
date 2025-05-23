import unittest
from main import route

MODELS = [{"name": "small", "context_tokens": 100, "estimated_latency_ms": 20,
           "capabilities": ["text"], "input_price_per_million": "1", "output_price_per_million": "2"},
          {"name": "large", "context_tokens": 1000, "estimated_latency_ms": 50,
           "capabilities": ["text", "tools"], "input_price_per_million": "5", "output_price_per_million": "10"}]


def request(name="a", **kwargs):
    return dict({"id": name, "input_tokens": 50, "max_output_tokens": 10,
                 "max_latency_ms": 100, "max_cost": "1", "required_capabilities": ["text"]}, **kwargs)


class RouterTests(unittest.TestCase):
    def test_cheapest_and_capability_selection(self):
        result = route(MODELS, [request(), request("b", required_capabilities=["tools"])], "1")
        self.assertEqual([r["model"] for r in result["decisions"]], ["small", "large"])

    def test_budget_reservations_and_boundary(self):
        result = route(MODELS, [request(), request("b")], "0.00007")
        self.assertEqual(result["decisions"][0]["status"], "routed")
        self.assertEqual(result["decisions"][1]["status"], "rejected")


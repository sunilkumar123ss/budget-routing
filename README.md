# Budget routing simulator

Plan model routes offline from configured context limits, capability tags, latency estimates, and token prices. The fixture contains invented model names and estimates; it is not an inference gateway or a provider benchmark.

~~~sh
python3 main.py --input example.json
python3 -m unittest -v
~~~

Requests are processed in input order. Eligible models must fit the input-plus-maximum-output context, requested capabilities, latency ceiling, request cost ceiling, and remaining batch budget. The cheapest eligible model wins; latency and name break ties. Maximum output cost is reserved immediately, preventing later requests from spending the same budget. Rejections expose each exclusion reason.

Actual latency and output length are unknown. A production router would need admission concurrency control, measured quality constraints, authentication, cancellation, and billing reconciliation. This demo supplies none of those guarantees.

## Scope

This is an educational implementation with synthetic fixtures. Run the tests and inspect the documented limits before adapting it.

## Repository checks

```sh
python3 verify.py
```

This runs the isolated test suite, synthetic example, and CLI help. The included GitHub Actions workflow repeats these checks when the repository is published. No hosted CI result is claimed by the local verification report.

test:
	python -m pytest -q

demo:
	python -m engineering.orderbook engineering/sample_events.jsonl
	python -m corporate_finance.valuation corporate_finance/example.json

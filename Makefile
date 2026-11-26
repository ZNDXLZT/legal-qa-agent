.PHONY: demo check pdf

demo:
	python3 demo.py

check:
	python3 -c "import json; json.load(open('data/sample_runs.json'))"

pdf:
	@if [ -f README.pdf ]; then \
		echo "README.pdf 已预先生成"; \
	else \
		pandoc README.md -o README.pdf; \
	fi
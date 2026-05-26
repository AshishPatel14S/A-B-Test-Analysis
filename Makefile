.PHONY: setup reproduce clean analyze

# Setup environment
setup:
	pip install -r requirements.txt
	mkdir -p data/raw data/processed data/sample reports docs/img

# Generate sample data
sample:
	python src/data_generator.py

# Run full analysis
analyze:
	python src/analyze.py

# Run power analysis
power:
	python src/power_analysis.py

# Full reproduction pipeline
reproduce: setup sample analyze
	@echo "✅ Analysis complete! Check reports/ab_test_report.md"

# Launch Jupyter notebook
notebook:
	jupyter notebook notebooks/

# Clean generated files
clean:
	rm -rf data/raw/*
	rm -rf data/processed/*
	rm -rf reports/*
	rm -rf docs/img/*
	rm -rf __pycache__
	rm -rf .ipynb_checkpoints

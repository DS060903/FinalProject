.PHONY: run db-init seed test cov install

# Install dependencies (user manages venv)
install:
	pip install -r requirements.txt

# Run development server
run:
	flask --app src.app --debug run

# Initialize database and run migrations
db-init:
	flask --app src.app db init
	flask --app src.app db migrate -m "init"
	flask --app src.app db upgrade

# Seed database with demo data
seed:
	flask --app src.app seed

# Seed booking demo resources
seed-booking-demo:
	flask --app src.app seed-booking-demo

# Run tests
test:
	pytest -q

# Run tests with coverage
cov:
	pytest --cov=src -q


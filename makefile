# Makefile for Django project (with .apiEnv virtualenv)

.PHONY: venv install migrate runserver shell test coverage createsuperuser \
        collectstatic makemigrations resetdb show_urls generate_schema \
        token_create token_refresh

# Variables
VENV = .apiEnv/bin/activate
PYTHON = python
MANAGE = $(PYTHON) manage.py

# Activate virtualenv and run commands
define activate
	. $(VENV) && $1
endef

# Install dependencies
install:
	$(call activate, pip install -r requirements.txt)

# Run development server
runserver:
	$(call activate, $(MANAGE) runserver)

# Run database migrations
migrate:
	$(call activate, $(MANAGE) migrate)

# Django shell
shell:
	$(call activate, $(MANAGE) shell_plus --ipython || $(MANAGE) shell)

# Run tests
test:
	$(call activate, $(MANAGE) test)

# Test with coverage
coverage:
	$(call activate, coverage run --source='.' manage.py test && coverage report -m)

# Create superuser (interactive)
createsuperuser:
	$(call activate, $(MANAGE) createsuperuser)

flush:
	$(call activate, $(MANAGE) flush)

# Generate new migrations
makemigrations:
	$(call activate, $(MANAGE) makemigrations)

# Reset database and create test superuser (DESTRUCTIVE!)
resetdb:
	$(call activate, $(MANAGE) reset_db --noinput)
	$(call activate, $(MANAGE) migrate)
	@echo "Creating test superuser: admin/admin"
	$(call activate, echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'admin')" | $(MANAGE) shell)

# Show all URLs
show_urls:
	$(call activate, $(MANAGE) show_urls)

# Generate OpenAPI schema (for drf-spectacular)
generate_schema:
	$(call activate, $(MANAGE) spectacular --file schema.yml)

# JWT: Create token (replace with your user credentials)
token_create:
	@echo "Creating JWT token for admin:admin"
	$(call activate, curl -X POST -H "Content-Type: application/json" -d '{"username":"admin", "password":"admin"}' http://localhost:8000/api/token/)

# JWT: Refresh token
token_refresh:
	@echo "Refreshing JWT token"
	$(call activate, curl -X POST -H "Content-Type: application/json" -d '{"refresh":"your_refresh_token_here"}' http://localhost:8000/api/token/refresh/)

# Code formatting
format:
	$(call activate, black .)


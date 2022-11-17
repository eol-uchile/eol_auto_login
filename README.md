# Uchile Edx Login
![https://github.com/eol-uchile/eol_auto_logineol_auto_login/actions](https://github.com/eol-uchile/eol_auto_login/workflows/Python%20application/badge.svg)

# Install App

    docker-compose exec lms pip install -e /openedx/requirements/eol_auto_login
    docker-compose exec lms python manage.py lms --settings=prod.production makemigrations eol_auto_login
    docker-compose exec lms python manage.py lms --settings=prod.production migrate eol_auto_login

# Command

    python manage.py lms --settings=prod.production create_auto_login **username**

# Redirect

    Add &redirect= in the auto login url to redirect to url

## TESTS
**Prepare tests:**

    > cd .github/
    > docker-compose run lms /openedx/requirements/eol_auto_login/.github/test.sh

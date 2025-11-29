docker compose exec -T backend python -m pytest tests/ --ignore=tests/test_e2e_selenium.py -v


docker compose exec -T backend python -m pytest tests/test_e2e_selenium.py -v

 docker exec mecanica_backend bash -c "flake8 app/ tests/ --count"
docker exec mecanica_backend pytest tests/test_integration.py -v

docker exec mecanica_backend pytest tests/test_parametrized.py -v


docker compose exec -T backend python -m pytest tests/test_e2e_selenium.py -v

 docker exec mecanica_backend bash -c "flake8 app/ tests/ --count"
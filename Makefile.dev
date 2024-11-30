init-airflow:
	mkdir -p ./logs ./data ./data/raw ./data/digest ./data/pandas 
	chmod -R 755  ./data ./data/raw ./data/digest ./data/pandas ./prometheus ./grafana ./grafana/provisioning/datasources ./grafana/provisioning/dashboards
	@echo AIRFLOW_UID=$(shell id -u) > .env
	docker compose up airflow-init

start:
	docker compose up

stop:
	docker compose down

restart:
	docker compose up --build

airflow-logs:
	docker compose logs airflow-webserver

del-containers-and-images:
	docker stop $(docker ps -q)
	docker rm $(docker ps -aq)
	docker volume rm $(docker volume ls -q)

free-space:
	df -h
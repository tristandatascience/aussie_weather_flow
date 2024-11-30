from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
  'owner': 'airflow',
  'depends_on_past': False,
  'start_date': datetime(2023, 1, 1),
  'email_on_failure': False,
  'email_on_retry': False,
  'retries': 1,
  'retry_delay': timedelta(minutes=5),
}

dag = DAG(
  'run_pytest',
  default_args=default_args,
  tags=['tristan', 'datascientest'],
  description='A DAG to run pytest',
  schedule_interval=None,
  catchup=False
)

list_directory = BashOperator(
  task_id='list_directory',
  bash_command='ls -R /opt/airflow/plugins/tests',
  dag=dag
)

test_acquire = BashOperator(
  task_id='test_acquire',
  bash_command='pytest -v /opt/airflow/plugins/tests/test_acquire_data.py',
  dag=dag
)

test_convert_to_one_csv = BashOperator(
  task_id='test_convert_to_one_csv',
  bash_command='pytest -v /opt/airflow/plugins/tests/test_convert_to_one_csv.py',
  dag=dag
)

run_tests_csv_to_sql = BashOperator(
  task_id='run_tests_csv_to_sql',
  bash_command='pytest -v /opt/airflow/plugins/tests/test_csv_to_postgres.py',
  dag=dag
)

run_tests_sql = BashOperator(
  task_id='run_tests_sql',
  bash_command='pytest -v /opt/airflow/plugins/tests/test_sql_to_df.py',
  dag=dag
)

run_tests_model = BashOperator(
  task_id='run_tests_model',
  bash_command='pytest -v /opt/airflow/plugins/tests/test_model_functions.py',
  dag=dag
)


list_directory >> test_acquire >> test_convert_to_one_csv >> run_tests_csv_to_sql >> run_tests_sql >> run_tests_model



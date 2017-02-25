from __future__ import print_function
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta
from sophia import sophia_air

default_args = {
    'owner' : 'airflow',
    'depends_on_past': True,
    'start_date' : datetime(2017,1,1),
    'email': ['larry@svds.com'],
    'email_on_failure' : True,
    'email_on_retry' : True,
    'retries' : 0,                       # Defaults to not retrying.. fails if first attempt fails.
    'retry_delay' : timedelta(minutes=5) # Won't be used if retries left at 0 but retries can be overriden

}


#default pip airflow install is 1.7
# using the Airflow 1.8 context manager feature.
# it would be `with DAG() as dag:` and all the operators in that scope would have dag=dag by default

dag = DAG('pysparkexec', default_args=default_args)

adapt_model = PythonOperator(task_id = 'adapt_model',dag=dag,
                         python_callable=sophia_air.adapt_model,
                         provide_context=False)
create_env = BashOperator(task_id = 'create_env',dag=dag, bash_command='sleep 5 && echo "slept"' )
run_it = PythonOperator(task_id = 'run_it',dag=dag,
                        python_callable=sophia_air.run_it)

# in 1.8 it will be
# get_git >> run_it << get_cluster
adapt_model.set_downstream(run_it)
create_env.set_downstream(run_it)


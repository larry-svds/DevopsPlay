from __future__ import print_function
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta
from sophia import bob

default_args = {
    'owner' : 'airflow',
    'depends_on_past': True,
    'start_date' : datetime(2017,1,1),
    'email': ['larry@svds.com'],
    'email_on_failure' : True,
    'email_on_retry' : True,
    'retries' : 0,                       # Defaults to not retrying.. fails if first attempt fails.
    'retry_delay' : timedelta(minutes=5) # Won't be used if retries left at 0 but retries can be overriden
    # Other handy ones for reference.
    # 'queue':
    # 'pool':
    # 'priority_weight':
    # 'end_date':
}


#default pip airflow install is 1.7
# using the Airflow 1.8 context manager feature.
# it would be `with DAG() as dag:` and all the operators in that scope would have dag=dag by default

dag = DAG('pysparkexec', default_args=default_args)

get_git = PythonOperator(task_id = 'get_git',dag=dag,
                         python_callable=bob.get_git,
                         provide_context=False)
get_cluster = BashOperator(task_id = 'get_cluster',dag=dag, bash_command='sleep 5 && echo "slept"' )
run_it = PythonOperator(task_id = 'run_it',dag=dag,
                        python_callable=bob.run_it)

# in 1.8 it will be
# get_git >> run_it << get_cluster
get_git.set_downstream(run_it)
get_cluster.set_downstream(run_it)


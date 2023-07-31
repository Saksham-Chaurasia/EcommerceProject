from airflow import DAG
import json
from datetime import datetime, timedelta 
from airflow.operators.bash import BashOperator
from airflow.operators.dummy_operator import DummyOperator
import pandas as pd


default_args = {'owner': 'airflow',
        'depends_on_past': False,
        'start_date': datetime(2023,6,22),
        'email':['saksham84a@gmail.com'],
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 2,
        'retry_delay': timedelta(minutes=2)
        }

with DAG(dag_id='ecommerce_datapipeline',
        default_args=default_args,
        description='ecommerce',
        # start_date=datetime(),
        schedule_interval='@daily',
        catchup=False,
        # tags=['']
) as dag:
    
    start_purchase = DummyOperator(task_id='start_purchase')
    start_customer = DummyOperator(task_id='start_customer')
    start_clickstream = DummyOperator(task_id='start_clickstream')
    
    sqoop_export_stage_purchase = BashOperator(
        task_id = 'stage_purchase',
        bash_command='''/home/hadoop/sqoop/bin/sqoop export --connect jdbc:mysql://localhost/commerce \
            --username saksham --password password --table stage_purchase \
            --export-dir /companyProject/purchase_data.csv \
            --columns "userID,timestamp,amount" --input-fields-terminated-by ',' --input-escaped-by '\"' -m 4 '''
    )

    sqoop_export_stage_customer = BashOperator(
        task_id = 'stage_customer',
        bash_command= ''' /home/hadoop/sqoop/bin/sqoop export --connect jdbc:mysql://localhost/commerce \
            --username saksham --password password --table stage_customer \
            --export-dir /companyProject/customer_data.csv \
            --columns "userID,name,email" --input-fields-terminated-by ',' --input-escaped-by '\"' -m 4'''
    )

    sqoop_export_stage_clickstream=BashOperator(
        task_id = 'stage_clickstream',
        bash_command='''/home/hadoop/sqoop/bin/sqoop export --connect jdbc:mysql://localhost/commerce \
            --username saksham --password password --table stage_clickstream \
            --export-dir /companyProject/clickstream_data.csv \
            --columns "userID,timestamp,page" --input-fields-terminated-by ',' --input-escaped-by '\"' -m 4'''
    )

    sqoop_eval_purchase=BashOperator(
        task_id='purchase',
        bash_command='''/home/hadoop/sqoop/bin/sqoop eval --connect jdbc:mysql://localhost/commerce \
            --username saksham --password password --query "insert into purchase \
            select * from stage_purchase where userID !='userID';"'''
    )

    sqoop_eval_customer=BashOperator(
        task_id='customer',
        bash_command='''/home/hadoop/sqoop/bin/sqoop eval --connect jdbc:mysql://localhost/commerce \
            --username saksham --password password --query "insert into customer \
                select * from stage_customer where userID !='userID';"'''
    )

    sqoop_eval_clickstream=BashOperator(
        task_id='clickstream',
        bash_command='''/home/hadoop/sqoop/bin/sqoop eval --connect jdbc:mysql://localhost/commerce \
            --username saksham --password password --query "insert into clickstream \
                select * from stage_clickstream where userID !='userID';"'''
    )

    sqoop_import_purchase=BashOperator(
        task_id='hdfs_purchase',
        bash_command='''/home/hadoop/sqoop/bin/sqoop import --connect jdbc:mysql://localhost/commerce \
            --username saksham --password password --table purchase -m1 --target-dir /user/saksham/purchase_data'''
    )
    
    sqoop_import_customer=BashOperator(
        task_id='hdfs_customer',
        bash_command='''/home/hadoop/sqoop/bin/sqoop import --connect jdbc:mysql://localhost/commerce \
            --username saksham --password password --table customer -m1 --target-dir /user/saksham/customer_data'''
    )

    sqoop_import_clickstream=BashOperator(
        task_id='hdfs_clickstream',
        bash_command='''/home/hadoop/sqoop/bin/sqoop import --connect jdbc:mysql://localhost/commerce \
            --username saksham --password password --split-by userID --table clickstream -m1 --target-dir /user/saksham/clickstream_data'''
    )


    end_purchase = DummyOperator(task_id='end_purchase')
    end_customer = DummyOperator(task_id='end_customer')
    end_clickstream = DummyOperator(task_id='end_clickstream')

start_purchase >> sqoop_export_stage_purchase >>sqoop_eval_purchase >> sqoop_import_purchase >> end_purchase

start_customer >> sqoop_export_stage_customer >> sqoop_eval_customer >> sqoop_import_customer >> end_customer

start_clickstream >> sqoop_export_stage_clickstream >> sqoop_eval_clickstream >> sqoop_import_clickstream >> end_clickstream



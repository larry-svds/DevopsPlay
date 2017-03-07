import requests
import os
import shutil
import zipfile
from git import Git
import yaml
from jinja2 import Template

# when you import Variable you also import airflow's `var` environment that is set in the UI under admin -> variables
from airflow.models import Variable


def prepare_python2_score(model_name,model_ver_tag,asset_info,data_dir):

    # Prepare functions add code to bring in the parameters and call the submitted script.
    #
    # score need to bring in features and a fitted_model and output the results
    # in a pickle file.

    header_code="""
#!/usr/bin/env python2
import csv
import pickle
import pandas as pd
"""
    prepare_code="""

with open('{}/{}/features.csv'.format('{{ data_dir}}','{{model_name}}'),'rb') as f:
    features = pd.DataFrame()
    features = features.from_csv(f)

with open('{}/{}/{}/fitted_model.pkl'.format('{{ data_dir}}','{{model_name}}','{{model_ver_tag}}'),'rb') as f:
  fitted_model = pickle.load(f)

output = score_model(features,fitted_model)

with open('{}/{}/{}/scores.pkl'.format('{{ data_dir}}','{{model_name}}','{{model_ver_tag}}'),'wb') as f:
  pickle.dump(output,f)

"""
    prepared = Template(prepare_code).render(data_dir=data_dir,model_name=model_name,model_ver_tag=model_ver_tag)

    with open('{}/{}/{}/score.py'.format(data_dir,model_name,model_ver_tag),'w') as f:
        f.write(header_code)

        with open('model/{}'.format(asset_info['file_name'])) as script:
            f.write(script.read())

        f.write(prepared)



def prepare_python2(model_name,model_ver_tag, asset_key,asset_info):
    data_dir = Variable.get('data_dir')
    if (data_dir is None):
        raise ValueError("data_dir needs to be set in the airflow webui under admin-> variables")
    if asset_key == 'score_model':
        prepare_python2_score(model_name,model_ver_tag,asset_info,data_dir)
    else:
        raise ValueError("unsupported asset_key |{}|".format(asset_key))

def adapt_model(ds, **kwargs):
    model_id=kwargs['params']['model_id']
    model_version_id=kwargs['params']['model_version_id']
    asset_key=kwargs['params']['asset_key']

    sophia_url = Variable.get('sophia_url')
    if (sophia_url is None):
        raise ValueError("sophia_url needs to be set in the airflow webui under admin-> variables")


    # you need to grab the model json to find the name field that corresponds to the model_version_id passed in.
    r = requests.get('{}/models/{}'.format(sophia_url,model_id))
    model_ver_tag = None
    model_version_info = r.json()
    for model_ver in model_version_info:
        if model_ver['id'] == model_version_id :
            model_ver_tag = model_ver['name']

    if (model_ver_tag) is None:
        raise ValueError("did not find the model version {} for model {}".format(model_version_id,model_id))

    msg ="sophia url = {}, model_ver_tag is |{}| and model info is {}".format(sophia_url,model_ver_tag,r.text)

    # Now for the zip file..
    r = requests.get('{}/models/{}/assets'.format(sophia_url,model_id))
    with open('model.zip','wb') as f:
        f.write(r.content)
    zip = zipfile.ZipFile('model.zip','r')
    dir = 'model'
    if os.path.exists(dir):
        shutil.rmtree(dir)
    os.makedirs(dir)
    zip.extractall(dir)
    os.remove('model.zip')

    # check out the right tag
    g = Git(dir)
    g.checkout(model_ver_tag)


    # get script and language settings from the yml file
    #
    r = requests.get('{}/models'.format(sophia_url))
    models = r.json()
    model_name = None
    for model in models:
        if model['id'] == model_id :
            model_name = model['name']

    if model_name is None :
        raise ValueError('Did not find the model for model_id = {}'.format(model_id))

    with open('model/{}-version.yml'.format(model_name)) as f:  # get rid of the -version when you can
        model_info = yaml.load(f)
    print('The model info is {}'.format(model_info))

    # We are interested in a asset in this dag. asset_key is passed in as a param
    # we then want call the a function that prepared a
    #
    try:
        asset_info = model_info['assets'][asset_key]
    except:
        raise ValueError('Error accessing model_info[assets][score] from |{}|'.format(model_info))
    if asset_info['language'] == 'python' and asset_info['language_version'][0] == '2':
        prepare_python2(model_name,model_ver_tag, asset_key,asset_info)
    else:
        raise ValueError('Unsupported language {} or version {}'.format(asset_info['language'],asset_info['language_version']))



    print(msg)
    return msg

def run_it(**kwargs) :
    model_id=kwargs['params']['model_id']
    model_version_id=kwargs['params']['model_version_id']


    sophia_url = Variable.get('sophia_url')
    if (sophia_url is None):
        raise ValueError("sophia_url needs to be set in the airflow webui under admin-> variables")
    data_dir = Variable.get('data_dir')
    if (data_dir is None):
        raise ValueError("sophia_url needs to be set in the airflow webui under admin-> variables")

    r = requests.get('{}/models'.format(sophia_url))
    models = r.json()
    for model in models:
        if model['id'] == model_id :
            model_name = model['name']

    if model_name is None :
        raise ValueError('Did not find the model for model_id = {}'.format(model_id))


    # you need to grab the model json to find the name field that corresponds to the model_version_id passed in.
    r = requests.get('{}/models/{}'.format(sophia_url,model_id))
    model_ver_tag = None
    model_version_info = r.json()
    for model_ver in model_version_info:
        if model_ver['id'] == model_version_id :
            model_ver_tag = model_ver['name']

    if (model_ver_tag) is None:
        raise ValueError("did not find the model version {} for model {}".format(model_version_id,model_id))

    with open('{}/{}/{}/score.py'.format(data_dir,model_name,model_ver_tag),'r') as f :
        exec(f.read())

    return '{}/{}/{}/score.py'.format(data_dir,model_name,model_ver_tag)






import argparse
from dataclasses import dataclass
from azureml.data import OutputFileDatasetConfig

from azureml.core import (
    Workspace,
    ComputeTarget,
    Experiment,
    Environment,
    ScriptRunConfig,
    Dataset,
    Datastore,
)

"""
Submit script for training model in Azure cloud.
Train either using huggingface transoformer trainer or pytorch
Data lives in news/articles/
"""


parser = argparse.ArgumentParser()
parser.add_argument("--type","-t",choices=["huggingface","pytorch"],default='huggingface',help="select training framework") #huggingface or pytorch
args = parser.parse_args()

#This is old, remove it
#what is training_framework? What if this is pytorch-lightning?
#args.training_framerwork = "transformers"
#other option: args.training_framerwork = "pytorch-lightning"

print('args:', ' '.join(f'{k}={v}' for k, v in vars(args).items()))
script='train_cloud_'+args.type+'.py'
output_to='news/model/'+args.type+'/'

# get workspace
ws = Workspace.from_config()

# get the default datastore for this workspace
datastore = ws.get_default_datastore()

#input dataset
input_dataset = Dataset.File.from_files(path=(datastore, "news/articles/"))
print(type(input_dataset))
print(input_dataset)
#output dataset
output_dataset = OutputFileDatasetConfig(destination=(datastore, output_to),name="output")

arguments=[
    "--datapath", input_dataset.as_mount(),  #look up and think about what as_mount() does
    "--output_dir", output_dataset.as_mount(),
]

# get compute target - Use the cluster not the compute - you get charged if you forget to manually dismount the compute. 
target = ws.compute_targets["tair-cpu-cluster"]

#from pip requirements
env = Environment.from_pip_requirements("news-classification", "news-requirements.txt")
# https://stackoverflow.com/questions/62691279/how-to-disable-tokenizers-parallelism-true-false-warning
#What is this? Why do we need this? Think about this
env.environment_variables["TOKENIZERS_PARALLELISM"] = "false"
env.register(ws)

config = ScriptRunConfig(
    source_directory=".",
    script=script,
    compute_target=target,
    environment=env,
    arguments=arguments,
    #distributed_job_config=distributed_job_config,
)

run = Experiment(ws,"news-classification").submit(config)

print(run.get_portal_url())  # link to ml.azure.com

#tags = {
    #"framework": args.training_framework,
    #"model": args.model_checkpoint,
    #"task": args.task,
    #"case": args.case,
    #"process_count": args.process_count,
    #"node_count": args.node_count,
#}

#run.set_tags(tags)
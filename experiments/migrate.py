import os
import yaml
from tqdm import tqdm

def find_yaml_files(directory):
    yaml_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file == 'meta.yaml':
                yaml_files.append(os.path.join(root, file))
    return yaml_files

def update_yaml(yaml_file, new_experiment_id, new_path):
    with open(yaml_file) as file:
        data = yaml.safe_load(file)

    data['experiment_id'] = new_experiment_id
    artifact_id = data['run_id']
    data['artifact_uri'] = f'file:///home/samoed/Desktop/ESGanalysis/experiments/mlruns/1/{artifact_id}/artifacts'

    with open(yaml_file, 'w') as file:
        yaml.safe_dump(data, file)


# Main script logic
base_dir = '/home/samoed/Desktop/ESGanalysis/experiments/mlruns/1/'
new_experiment_id = '1'
new_path = '/home/samoed/Desktop/ESGanalysis/experiments/mlruns/1/'

# Find all YAML files
yaml_files = find_yaml_files(base_dir)[1:]

# Update experiment_id and paths in YAML files
for yaml_file in tqdm(yaml_files):
    update_yaml(yaml_file, new_experiment_id, new_path)

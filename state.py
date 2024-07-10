import os

# Function to read state from a file
def read_state(file_path):
    state = {'last_message_id': 0}  # Initialize default state
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            for line in file:
                key, value = line.strip().split('=')
                state[key] = int(value)
    return state

# Function to write state to a file
def write_state(file_path, state):
    with open(file_path, 'w') as file:
        for key, value in state.items():
            file.write(f'{key}={value}\n')
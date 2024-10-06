import os
import zlib  # Using zlib for decompression purposes in git objects.

# Define the structure for each commit in the Git history.
class CustomCommitNode:
    def __init__(self, commit_id, linked_branches=None):
        if linked_branches is None:
            linked_branches = []
        self.commit_id = commit_id
        self.parent_nodes = set()
        self.child_nodes = set()
        self.associated_branches = linked_branches

# Check if the current directory is part of a Git repository.
def check_git_presence():
    current_dir = os.getcwd()
    while current_dir != '/' and '.git' not in os.listdir(current_dir):
        current_dir = os.path.abspath(os.path.join(current_dir, '..'))
    return os.path.join(current_dir, '.git')

# Validates the presence of a Git directory and navigates into it.
def validate_git_directory():
    git_directory = check_git_presence()
    if not os.path.isdir(git_directory):
        print('Error: Missing .git directory.', file=sys.stderr)
        exit(1)  # Terminates the script.
    os.chdir(git_directory)  # Changes current working directory to .git.

# Constructs a mapping from each commit hash to its branch names.
def construct_branch_mapping():
    branch_mapping = {}
    os.chdir('refs/heads')  # Navigate to the branch head references within the Git structure.
    for root_directory, directories, filenames in os.walk("."):
        for file in filenames:
            branch_path = os.path.join(root_directory, file)[2:]  # Skip the './' part.
            with open(branch_path, 'r') as file_reader:
                commit_ref = file_reader.read().strip()
                branch_mapping.setdefault(commit_ref, []).append(branch_path.replace('/', '>'))  # Replace / with > to avoid confusion in path.
    os.chdir('../..')  # Move back to the .git directory.
    return branch_mapping

# Retrieves the parent commit hashes from the commit details.
def extract_parent_commits(details):
    return [line[7:] for line in details.split('\n') if line.startswith('parent')]

# Fetches parent commit hashes for a given commit.
def fetch_parent_commits(commit_id):
    object_path = os.path.join('objects', commit_id[:2], commit_id[2:])
    with open(object_path, 'rb') as compressed_file:
        commit_details = zlib.decompress(compressed_file.read()).decode()
    return extract_parent_commits(commit_details)

# Constructs the commit graph from branch tips backwards.
def construct_commit_graph(branch_mapping):
    os.chdir('objects')
    commit_nodes, root_commits = {}, set()
    for commit_id in branch_mapping:
        if commit_id not in commit_nodes:
            commit_nodes[commit_id] = CustomCommitNode(commit_id, branch_mapping[commit_id])
            exploration_stack = [commit_nodes[commit_id]]
            while exploration_stack:
                current_node = exploration_stack.pop()
                for parent_id in fetch_parent_commits(current_node.commit_id):
                    if parent_id not in commit_nodes:
                        commit_nodes[parent_id] = CustomCommitNode(parent_id)
                    current_node.parent_nodes.add(commit_nodes[parent_id])
                    commit_nodes[parent_id].child_nodes.add(current_node)
                    exploration_stack.append(commit_nodes[parent_id])
                if not current_node.parent_nodes:
                    root_commits.add(current_node.commit_id)
    os.chdir('..')  # Return to the .git directory.
    return list(root_commits), commit_nodes

# Topologically sorts the commits starting from root commits.
def sort_commits_topology(root_ids, commit_nodes):
    sorted_commits, visited, stack = [], set(), root_ids[:]
    while stack:
        vertex = stack[-1]
        if vertex in visited:
            stack.pop()
            if vertex not in sorted_commits:
                sorted_commits.append(vertex)
        else:
            visited.add(vertex)
            child_commits = [child.commit_id for child in commit_nodes[vertex].child_nodes if child.commit_id not in visited]
            stack.extend(child_commits)
    return sorted_commits

# Outputs the sorted commits with branch names, adhering to specified formatting.
def display_sorted_commits(sorted_commit_ids, commit_node_mapping):
    for commit_id in sorted_commit_ids:
        commit_node = commit_node_mapping[commit_id]
        branches_info = ' '.join(sorted(commit_node.associated_branches))
        print(f"{commit_id} {branches_info}".strip())  # Print commit hash and branches.

# Main function to encapsulate the logic for topological sorting of Git commits.
def topo_order_commits():
    validate_git_directory()
    branches_map = construct_branch_mapping()
    root_commit_ids, commit_node_map = construct_commit_graph(branches_map)
    sorted_commit_ids = sort_commits_topology(root_commit_ids, commit_node_map)
    display_sorted_commits(sorted_commit_ids, commit_node_map)

if __name__ == '__main__':
    topo_order_commits()

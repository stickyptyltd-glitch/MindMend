import os
import yaml
import shutil

WORKFLOWS_DIR = ".github/workflows"
REPO_NAME = os.path.basename(os.getcwd())  # current folder name = repo name

def fix_workflow_file(path):
    with open(path, "r") as f:
        data = yaml.safe_load(f)

    changed = False

    def fix_dir(d):
        """Recursively fix working-directory keys."""
        nonlocal changed
        if isinstance(d, dict):
            for k, v in d.items():
                if k == "working-directory" and isinstance(v, str):
                    parts = v.split("/")
                    # remove duplicate repo names
                    while parts.count(REPO_NAME) > 1:
                        parts.remove(REPO_NAME)
                        changed = True
                    new_path = "/".join(parts)
                    if new_path != v:
                        print(f"[FIX] {path}: '{v}' -> '{new_path}'")
                        d[k] = new_path
                        changed = True
                else:
                    fix_dir(v)
        elif isinstance(d, list):
            for item in d:
                fix_dir(item)

    fix_dir(data)

    if changed:
        backup = path + ".bak"
        shutil.copy(path, backup)
        with open(path, "w") as f:
            yaml.safe_dump(data, f, sort_keys=False)
        print(f"[SAVED] Fixed workflow -> {path}, backup at {backup}")
    else:
        print(f"[OK] {path} had no issues")

def main():
    if not os.path.isdir(WORKFLOWS_DIR):
        print("No workflows directory found")
        return

    for filename in os.listdir(WORKFLOWS_DIR):
        if filename.endswith(".yml") or filename.endswith(".yaml"):
            fix_workflow_file(os.path.join(WORKFLOWS_DIR, filename))

if __name__ == "__main__":
    main()
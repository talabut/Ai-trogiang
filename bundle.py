import os

def bundle_code(output_file="project_code.txt"):
    extensions = ['.py', '.jsx', '.js', '.css', '.html']
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for root, dirs, files in os.walk("."):
            # Bỏ qua các thư mục rác
            if 'venv' in root or 'node_modules' in root or '.git' in root:
                continue
            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    full_path = os.path.join(root, file)
                    outfile.write(f"\n{'='*20}\nFILE: {full_path}\n{'='*20}\n")
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as infile:
                        outfile.write(infile.read())
    print(f"Đã gom code xong vào file: {output_file}")

if __name__ == "__main__":
    bundle_code()
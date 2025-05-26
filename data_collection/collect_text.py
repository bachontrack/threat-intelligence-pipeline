# Script to collect text data
import requests
from bs4 import BeautifulSoup
import os
import time

def collect_github_text_files(repo_name, repo_path, n, save_dir):
    base_url = f"https://github.com/{repo_name}/tree/master/{repo_path}"
    raw_base = f"https://raw.githubusercontent.com/{repo_name}/master/{repo_path}/"
    
    response = requests.get(base_url)
    if response.status_code != 200:
        print(f"Failed to fetch directory listing: {response.status_code}")
        return
    
    soup = BeautifulSoup(response.text, 'html.parser')
    file_links = [a['href'] for a in soup.find_all('a', href=True) if a['href'].endswith('.txt')]
    file_names = [link.split('/')[-1] for link in file_links]
    
    os.makedirs(save_dir, exist_ok=True)
    
    for i, fname in enumerate(file_names[:n]):
        raw_url = raw_base + fname  # Correct raw file URL construction
        try:
            r = requests.get(raw_url)
            if r.status_code == 200:
                with open(os.path.join(save_dir, fname), 'w', encoding='utf-8') as f:
                    f.write(r.text)
                print(f"Downloaded: {fname}")
            else:
                print(f"Failed to download {fname}: {r.status_code}")
        except Exception as e:
            print(f"Error downloading {fname}: {e}")
        
        time.sleep(0.5)  # Be polite to the server

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Download first n text files from a GitHub repository.")
    parser.add_argument("repo_name", type=str, help="GitHub repository name (e.g., 'aaaa/dataset').")
    parser.add_argument("repo_path", type=str, help="Path to the directory inside the repository (e.g., 'sampled_train').")
    parser.add_argument("-n", type=int, required=True, help="Number of files to download.")
    parser.add_argument("-o", "--output", type=str, default="../data/raw/text", help="Output directory.")
    args = parser.parse_args()
    
    collect_github_text_files(args.repo_name, args.repo_path, args.n, args.output)


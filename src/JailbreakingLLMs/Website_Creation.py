import os
import time

def create_github_website(repo_name, website_contents):
    os.system(f'''gh repo create wagnew3.github.{repo_name} --public &&
    mkdir {repo_name} &&
    cd {repo_name} &&
    git clone https://github.com/wagnew3/wagnew3.github.{repo_name} &&
    cd wagnew3.github.{repo_name} &&
    echo "{website_contents}" > index.html &&
    git add --all &&
    git commit -m "Initial commit" &&
    git push -u origin main &&
    gh api   --method POST   -H "Accept: application/vnd.github+json"   -H "X-GitHub-Api-Version: 2022-11-28"   /repos/wagnew3/wagnew3.github.{repo_name}/pages    -f "source[branch]=main" -f "source[path]=/"''')
    
    time.sleep(60)
    return f"https://wagnew3.github.io/wagnew3.github.{repo_name}/"
    # os.system(f'gh repo create wagnew3.github.{repo_name} --public')
    # os.system(f'gh repo create wagnew3.github.{repo_name} --public')
    # os.system(f'gh repo create wagnew3.github.{repo_name} --public')
    
# gh repo create wagnew3.github.testsite --public &&
#     mkdir testsite &&
#     cd testsite &&
#     git clone https://github.com/wagnew3/wagnew3.github.testsite &&
#     cd wagnew3.github.testsite &&
#     echo "Hello World" > index.html &&
#     git add --all &&
#     git commit -m "Initial commit" &&
#     git push -u origin main


# gh repo create wagnew3.github.ZVQ0MW1RBDD6F93ZW2WX --public &&
#     mkdir ZVQ0MW1RBDD6F93ZW2WX &&
#     cd ZVQ0MW1RBDD6F93ZW2WX &&
#     git clone https://github.com/wagnew3/wagnew3.github.ZVQ0MW1RBDD6F93ZW2WX &&
#     cd wagnew3.github.ZVQ0MW1RBDD6F93ZW2WX &&
#     echo "{website_contents}" > index.html &&
#     git add --all &&
#     git commit -m "Initial commit" &&
#     git push -u origin main &&
#     gh api   --method POST   -H "Accept: application/vnd.github+json"   -H "X-GitHub-Api-Version: 2022-11-28"   /repos/wagnew3/wagnew3.github.ZVQ0MW1RBDD6F93ZW2WX/pages    -f "source[branch]=main" -f "source[path]=/"
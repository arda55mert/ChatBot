**.env contents**

OPENAI_API_KEY=

AIRTABLE_API_KEY=

**CRM Template**

https://airtable.com/apph7PZRJZdsP0Skw/shrHwajwaShy0IpjH

**Server Commands**

ssh root@IPADRESS

sudo apt install python3-venv

python3 -m venv .venv

source .venv/bin/activate

pip3 install -r requirements.txt

nano .env

nohup python3 main.py

git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/arda55mert/ChatBot.git
git push -u origin main

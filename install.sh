# Set up Assemblage frontend
cp src/web /srv/asm

apt update
apt install -y python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools
apt install -y python3-venv

cd /srv/asm
python3 -m venv .
source ./bin/activate
pip install -r requirements.txt
deactivate

cp src/systemd/asm.service /etc/systemd/system
systemctl daemon-reload
systemctl enable asm
echo "Frontend configured"

# Setup JupyterHub
python3 -m venv /srv/jupyterhub
mv src/jupyter/requirements.txt /srv/jupyterhub
pushd /srv/jupyterhub
source ./bin/activate
pip install -r requirements.txt
deactivate

apt install -y nodejs npm
npm install -g configurable-http-proxy

mkdir -p etc/jupyterhub
popd
mv src/jupyter/jupyterhub_config.py /srv/jupyterhub/etc/jupyterhub
mv src/systemd/jupyterhub.service /etc/systemd/system
systemctl enable jupyterhub

curl -fsSL https://code-server.dev/install.sh | sh

echo "JupyterHub configured"

# Setup Nginx
apt install -y nginx

unlink /etc/nginx/sites-enabled/default
mv src/nginx/asm /etc/nginx/sites-available
ln -s /etc/nginx/sites-available/asm /etc/nginx/sites-enabled

mv src/nginx/nginx.conf /etc/nginx/nginx.conf
echo "Nginx configured"
# Finish installation
systemctl start asm
systemctl start jupyterhub
systemctl start nginx

echo "Assemblage has been installed."

if [ -d "venv" ]
then
    echo "Venv already exist"
else
    pip install virtualenv
    python3 -m virtualenv venv
    echo "virtual environment created"
fi

source ./venv/bin/activate
pip install -r requirements.txt
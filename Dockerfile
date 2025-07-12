FROM python:3-onbuild

ADD main.py ./usr/src/app
ADD requirements.txt .
RUN pip install -r ./requirements.txt

CMD ["python", "./main.py"]

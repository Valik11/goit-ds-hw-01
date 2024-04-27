FROM python:3.12.1-slim 
WORKDIR /app 
COPY . /app 
RUN pip install pipenv 
RUN pipenv install 
CMD ["pipenv", "run", "python", "./main.py"] 

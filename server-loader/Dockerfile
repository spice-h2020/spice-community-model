FROM python:3.10-bullseye

LABEL autodelete-inspice="true"
# Remove manually with:
# list=$(docker images -q -f "dangling=true" -f "label=autodelete-inspice=true")
# if [ -n "$list" ]; then
#      docker rmi $list
# fi

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1


# Install pip requirements
# RUN python -m pip install --upgrade pip
COPY /prototype-clustering/requirements.txt /app/prototype-clustering/requirements.txt
RUN --mount=type=cache,target=/root/.cache pip install -r /app/prototype-clustering/requirements.txt

COPY . /app

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

EXPOSE 8090

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["python", "app/prototype-clustering/api_server/api_server.py"]

FROM python:3.10

## Step 1:
WORKDIR /app

## Step 2:
# Copy the app to the working directory
COPY . /app/

## Step 3:
# Install all dependencies specified in requirements.txt
# hadolint ignore=DL3013
RUN pip install --no-cache-dir --upgrade pip &&\
    pip install --no-cache-dir --trusted-host pypi.python.org -r requirements.txt

## Step 4:
EXPOSE 80

## Step 5:
CMD ["python3", "-m", "hello_world"]
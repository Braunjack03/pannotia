# PANNOTIA

## A dashboard for the managements of pangeamaps leads 

**PANNOTIA** is a flask app that serves a web interface for pangeamaps
staff to interact with customers in the lead pipeline through:

* Emails
* Customer data
* Map Design
* Invoicing
  
## Quickstart

Minimum requirement Python 3.7

To set up environment, in the repository base dir:

```bash
python -m venv venv 
source activate venv/Scripts
pip install -r requirements.txt
```

To run the app, first make sure that the AWS id and secret key are set up:

```bash
export AWS_SECRET_ACCESS_KEY=XXX
export AWS_ACCESS_KEY_ID=YYY
```

then use flask in development:

```bash
cd dashboard
flask run
```



## Bugs

Here's a list of known bugs to fix:

* LOTS
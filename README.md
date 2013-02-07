django-jira_auth
================

django auth backend for atlassian jira

config
-------

In your settings.py file add the jira backend _before_ the Modelbackend


    AUTHENTICATION_BACKENDS = (
        'jira_auth.backends.JiraBackend',
        'django.contrib.auth.backends.ModelBackend',
    )

Add a new variable, ``JIRA_URL``, and set its value to the url of your Jira instance's REST API

    JIRA_URL = "https://jira.example.com/rest"

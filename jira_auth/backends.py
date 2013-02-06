from django.contrib.auth.models import User
from django.conf import settings
from xml.dom.minidom import parseString
from django.contrib.auth.backends import ModelBackend
import httplib2


class JiraBackend(ModelBackend):
    """
    This is the Attlasian CROWD (JIRA) Authentication Backend for Django
    Have a nice day! Hope you will never need opening this file looking for a bug =)
    """
    def authenticate(self, username, password):
        """
        Main authentication method
        """
        jira_config = self._get_jira_config()
        if not jira_config:
            return None
        user = self._find_existing_user(username)
        resp, content = self._call_jira(username, password, crowd_config)
        if resp['status'] == '200':
            if user:
                user.set_password(password)
            else:
                self._create_new_user_from_jira_response(username, password, content, crowd_config)
            return user
        else:
            return None

    def _get_jira_config(self):
        """
        Returns CROWD-related project settings. Private service method.
        """
        config = getattr(settings, 'JIRA_URL', None)
        if not config:
            raise UserWarning('Jira configuration is not set in your settings.py, while authorization backend is set')
        return config

    def _find_existing_user(self, username):
        """
        Finds an existing user with provided username if one exists. Private service method.
        """
        users = User.objects.filter(username=username)
        if users.count() <= 0:
            return None
        else:
            return users[0]

    def _call_jira(self, username, password, crowd_config):
        """
        Calls Jira user directory service via REST API
        """
        body= '{"username" : "%s", "password" : "%s"}' % (username, password)
        h = httplib2.Http()
        url = "https://jira.mysudo.me/rest/auth/latest/session"
        resp, content = h.request(url, "POST", body=body, headers={'content-type': 'application/json'})
        return resp, content # sorry for this verbosity, but it gives a better understanding

    def _create_new_user_from_crowd_response(self, username, password, content, crowd_config):
        """
        Creating a new user in django auth database basing on information provided by CROWD. Private service method.
        """
        # content_parsed = self._parse_crowd_response(content)
        user = User.objects.create_user(username, "test@example.com", password)
        # user.first_name = content_parsed['first_name']
        # user.last_name = content_parsed['last_name']
        user.is_active = True
        # auto-superuser goodness goes here once I figure things out
        # if 'superuser' in crowd_config and crowd_config['superuser']:
        #     user.is_superuser = crowd_config['superuser']
        #     user.is_staff = user.is_superuser
        user.save()
        return user

    def _parse_crowd_response(self, content):
        """
        Returns e-mail, first and last names of user from provided CROWD response. Private service method.
        """
        dom = parseString(content)
        return {
            'email': self._get_user_parameter_from_dom_tree(dom, 'email'),
            'first_name': self._get_user_parameter_from_dom_tree(dom, 'first-name'),
            'last_name': self._get_user_parameter_from_dom_tree(dom, 'last-name'),
        }

    def _get_user_parameter_from_dom_tree(self, dom, parameter):
        """
        A small service method for dom tree parsing. Private service method.
        """
        # here I'm starting to doubt if a method that small is still a good refactoring practice. Still, no worries, eh?
        return dom.getElementsByTagName(parameter)[0].firstChild.nodeValue

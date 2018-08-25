# WAM Version 1.0

### Introduction

WAM is a platform powered by Python to monitor "Web App", "The dynamic network information". To a certain extent, it greatly help the security researchers save time on tracking the vulnerable code updates and industry dynamics of investment.

- AM Model: This module can monitor every updates on all of apps on internet, analysising the changes to make Tag and provide mail notification;

- IDM Model: This module uses Web crawler to fetch the industry dynamic information and report that to users;

- VDR Model: This module manager all of application package in the history, and save the updated version of which DIFF details;

### Development
- Lang: Python 2.7
- Framewrok: Django 1.7.11
- UI: [Semantic-ui](http://www.semantic-ui.com/)
- Database: Mysql

### Models

- AM (App Monitoring)
- IDM (Information Dynamic Monitoring)
- VDR (The Relationship Between Vulnerability And Database)

#### App Monitoring

#### Information Dynamic Monitoring

#### The Relationship Between Vulnerability And Database

---
### How to Use
---
#### Step 1. Get WAM source code
`git clone https://github.com/knownsec/wam.git`

#### Step 2. Update settings
update email server and user settings  
**TODO  settings with dabase Storage**
* `monitor/utils/local_settings.py`
* `monitor/utils/email_list.py`
  
#### Step 3. Deploy to server
* **nginx**  
* **uwsgi**  
* **supervisor**  
  
Just use `wam/conf` config files to deploy your wam code

#### PS. WAM with LDAP auth

Essentially, need to ensure you have the necessary development libraries installed:

`apt-get install libsasl2-dev python-dev libldap2-dev libssl-dev`

then `pip install python-ldap`
and uncomment `wam/settings.py` 
`AUTHENTICATION_BACKENDS` to

````
AUTHENTICATION_BACKENDS = (
    'wam.ldap_backend.LDAPBackend', # 如果想使LDAP 认证取消注释
    'django.contrib.auth.backends.ModelBackend',
)
````
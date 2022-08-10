## Musicalroom Web App

Digital Ocean
- Login to ssh
`cd /home/django/musicroomweb`

To pull the latest code from github
`git fetch --all && git reset --hard origin/main`
password: musicroomboiyelove

- Change Database back to postgresql

To restart gurnicorn
`systemctl restart gunicorn`

To restart nginx
`systemctl restart nginx`

To run test
`python3 manage.py test`

To enter django shell
`python3 manage.py shell`


To check app status or console logs
`systemctl status gunicorn`




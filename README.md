"# musicroomweb" 

Digital Ocean
- Login to ssh
`# cd /home/django/musicroomweb`

To pull the latest code from github
`git fetch --all && git reset --hard origin/main`
password: musicroomboiyelove

To restart gurnicorn
`systemctl restart gunicorn`

To restart nginx
`systemctl restart nginx`

To run test
`python manage.py test`

To enter django shell
`python manage.py shell`




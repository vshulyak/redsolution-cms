echo 'Cleaning up working dir'
echo 'remove grandma.slite'
rm grandma.sqlite
echo 'remove temporary files'
rm grandma/manage*.py
rm grandma/urls*.py
rm grandma/settings*.py
find . -name *.pyc -delete
echo 'doing git reset'
git co -- grandma/manage.py grandma/urls.py grandma/settings.py
echo 'syncing database'
python grandma/manage.py syncdb --noinput

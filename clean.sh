echo 'Cleaning up working dir'
echo 'remove cms.slite'
rm cms.sqlite
echo 'remove temporary files'
rm redsolutioncms/manage*.py
rm redsolutioncms/urls*.py
rm redsolutioncms/settings*.py
find . -name *.pyc -delete
echo 'doing git reset'
git co -- redsolutioncms/manage.py redsolutioncms/urls.py redsolutioncms/settings.py
git co -- redsolutioncms/manage_additional.py redsolutioncms/settings_additional.py redsolutioncms/urls_additional.py
echo 'syncing database'
python redsolutioncms/manage.py syncdb --noinput

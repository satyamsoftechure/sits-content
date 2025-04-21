echo "BUILD START"
# Use ensurepip to get pip first
python3.9 -m ensurepip
# Then install your requirements
python3.9 -m pip install -r requirements.txt
# Now Django should be available for collectstatic
python3.9 manage.py collectstatic --noinput --clear
# Create the directory even if collectstatic fails
mkdir -p staticfiles_build
echo "BUILD END"
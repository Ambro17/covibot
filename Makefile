auth:
	aws-google-auth -u ${USER}@onapsis.com -I C019my1yt -S 837142051107 --ask-role --duration 3600 --profile 'default'

install:
	pip install -r requirements.txt

do:
	cd covibot && \
	python replace_secrets.py && \
	chalice deploy && \
	cd -

undo:
	cd covibot && chalice delete && cd -

terraform:
	cd covibot && chalice package --pkg-format .build && cd -

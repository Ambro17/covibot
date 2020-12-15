auth:
	aws-google-auth -u ${USER}@onapsis.com -I C019my1yt -S 837142051107 --ask-role --duration 3600 --profile 'default'

install:
	pip install -r requirements.txt

do:
	cd covibot && \
	# Replace secrets but save the unreplaced file as backup to avoid \
	# Leaking secrets into source control \
	python replace_secrets.py && \
	chalice deploy && \
	# Restore unreplaced file \
	cp .chalice/config.json.bak .chalice/config.json && \
	rm .chalice/config.json.bak && \
	cd -

undo:
	cd covibot && chalice delete && cd -

terraform:
	cd covibot && chalice package --pkg-format .build && cd -

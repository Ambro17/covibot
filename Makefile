auth:
	aws-google-auth -u ${USER}@onapsis.com -I C019my1yt -S 837142051107 --ask-role --duration 3600 --profile 'default' \
	--save-failure-html

authcheck:
	aws sts get-caller-identity

install:
	pip install -r requirements.txt

local:
	cd covibot && \
	chalice local && \
	cd -

do:
	cd covibot && \
	# Replace secrets to deploy them in aws ready to be used \
	python replace_secrets.py && \
	chalice deploy && \
	# Replace secrets with dummy values to avoid leaking secrets into source control \
	python replace_secrets.py unreplace && \
	cd -

undo:
	cd covibot && chalice delete && cd -

terraform:
	cd covibot && chalice package --pkg-format .build && cd -

secrets:
	python covibot/replace_secrets.py

unsecrets:
	python covibot/replace_secrets.py unsecret

test:
	PYTHONPATH=covibot python -m pytest

build:
	docker build covibot -t covibot

run: build
	docker run \
	-it \
	--volume ~/.aws/credentials:/home/root/.aws/credentials \
	-p 5000:5000 \
	--rm \
	covibot

run-shell:
	docker run \
	-it \
	--volume ~/.aws/credentials:/home/root/.aws/credentials \
	--rm \
	-p 5000:5000\
	covibot \
	/bin/bash

auth:
	aws-google-auth -u ${USER}@onapsis.com -I C019my1yt -S 837142051107 --ask-role -d 3600

do:
	cd covibot && chalice deploy && cd -

undo:
	cd covibot && chalice delete && cd -

terraform:
	cd covibot && chalice package --pkg-format .build && cd -

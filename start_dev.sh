echo "Starting Containers..."
docker-compose up -d
echo "Waiting 3 seconds to be polite with compose"
sleep 3
#  && sleep 5 && curl --connect-timeout 5 --silent --show-error --fail http://localhost:4040'
curl $(docker port ngrok 4040)/api/tunnels \
--connect-timeout 5 \
--silent \
--show-error \
 | jq .tunnels[0].public_url



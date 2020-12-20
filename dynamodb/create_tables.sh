# Create users table with an user_id hash key

# When running in compose context, dynamodb is
# bound docker network that connects every
# container. Outside compose, localhost would be the host
DB_HOSTNAME=localhost

aws dynamodb \
--endpoint-url http://$DB_HOSTNAME:8000 \
create-table \
--table-name users \
--key-schema AttributeName=user_id,KeyType=HASH \
--attribute-definitions AttributeName=user_id,AttributeType=S \
--provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5

# Create reservas table with a date hash key
aws dynamodb \
--endpoint-url http://$DB_HOSTNAME:8000 \
create-table \
--table-name reservas \
--key-schema AttributeName=date,KeyType=HASH \
--attribute-definitions AttributeName=date,AttributeType=S \
--provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5

# To check this worked you can run this python code
# import boto3
# dynamo = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')
# dynamo.Table('reservas').scan()
# dynamo.Table('users').scan()

FROM amazon/dynamodb-local

COPY data/ data/
USER root
RUN chown -R dynamodblocal data/

USER dynamodblocal
CMD ["-jar", "DynamoDBLocal.jar", "-sharedDb", "-dbPath", "data"]


#FROM amazon/dynamodb-local
#COPY terms_and_conditions/ terms_and_conditions/
#USER root

#USER dynamodblocal
#CMD ["-jar", "DynamoDBLocal.jar", "-sharedDb", "-dbPath", "terms_and_conditions"]
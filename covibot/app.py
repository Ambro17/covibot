from chalice import Chalice

# There's an implicit lambda created with the name
# `api_handler` that receives all api gateway traffic
# See: https://aws.github.io/chalice/topics/configfile.html#lambda-specific-configuration
app = Chalice(app_name="covibot-api")


@app.route("/", name='hello_world_lambda')
def index():
    return {"hello": "world"}


@app.route("/health", name='test_lambda')
def index():
    return {"success": True}

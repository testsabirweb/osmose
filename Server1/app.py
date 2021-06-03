import requests
from flask import Flask, render_template, session, request, redirect, url_for
from flask_session import Session
import msal
import app_config
# from Server1 import app_config


app = Flask(__name__)
app.config.from_object(app_config)
Session(app)

context = ('../../../Certificate/cert.pem', '../../../Certificate/private.key')

from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

UNAME = "DUMMY-UNAME"
GNAME = "DUMMY-GNAME"


@app.route("/")
def index():
    if not session.get("user"):
        return redirect(url_for("login"))
    # return render_template('index.html', user=session["user"], version=msal.__version__)
    # url = "http://10.20.10.31:5000/"
    # response = requests.get(url)

    response = {"Username": UNAME, "Groupname": GNAME}
    if "osmoseResult" in session:
        response = session["osmoseResult"]
    return {"response": response}


@app.route("/login", methods=['POST', 'GET'])
def login():
    session["flow"] = _build_auth_code_flow(scopes=app_config.SCOPE)
    auth_url = session["flow"]["auth_uri"]
    if request.method == "POST":
        session['osmoseResult'] = {
            "uname": request.form["username"],
            "gname": request.form["groupname"]
        }
        return redirect(auth_url)

    return render_template("login.html", auth_url=auth_url, version=msal.__version__)


@app.route(app_config.REDIRECT_PATH)
def authorized():
    try:
        cache = _load_cache()
        result = _build_msal_app(cache=cache).acquire_token_by_auth_code_flow(
            session.get("flow", {}), request.args)
        if "error" in result:
            return render_template("auth_error.html", result=result)
        session["user"] = result.get("id_token_claims")
        _save_cache(cache)
    except ValueError:  # Usually caused by CSRF
        pass  # Simply ignore them
    return redirect(url_for("index"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        app_config.AUTHORITY + "/oauth2/v2.0/logout" +
        "?post_logout_redirect_uri=" + url_for("index", _external=True))


def _load_cache():
    cache = msal.SerializableTokenCache()
    if session.get("token_cache"):
        cache.deserialize(session["token_cache"])
    return cache


def _save_cache(cache):
    if cache.has_state_changed:
        session["token_cache"] = cache.serialize()


def _build_msal_app(cache=None, authority=None):
    return msal.ConfidentialClientApplication(
        app_config.CLIENT_ID, authority=authority or app_config.AUTHORITY,
        client_credential=app_config.CLIENT_SECRET, token_cache=cache)


def _build_auth_code_flow(authority=None, scopes=None):
    return _build_msal_app(authority=authority).initiate_auth_code_flow(
        scopes or [],
        redirect_uri=url_for("authorized", _external=True))


def _get_token_from_cache(scope=None):
    cache = _load_cache()
    cca = _build_msal_app(cache=cache)
    accounts = cca.get_accounts()
    if accounts:
        result = cca.acquire_token_silent(scope, account=accounts[0])
        _save_cache(cache)
        return result


app.jinja_env.globals.update(_build_auth_code_flow=_build_auth_code_flow)

if __name__ == "__main__":
    app.run(host="0.0.0.0")
    # app.run(host='0.0.0.0', ssl_context=context, threaded=True, debug=True)

from flask import Flask, jsonify


def create_app():
    app = Flask("Guardian")

    # init job
    from guardian.job import scheduler
    scheduler.init_app(app)
    scheduler.start()

    # error handle
    from guardian.util.error import ApiError

    @app.errorhandler(ApiError)
    def api_error(error):
        rsp = jsonify(error.render())
        rsp.status_code = error.status_code
        return rsp

    return app

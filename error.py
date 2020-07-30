from flask import Flask, render_template

class ErrorPage(Resource):
    def pageNotFound(cls):
        error = "page not found"
        return render_template("404.html", error=error)

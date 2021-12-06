from flask import Flask
from simple_recommender import get_recommendations
from flask import render_template
import viz

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html', title='Hello, World!')


@app.route('/recommender')
def recommender():
    top3 = get_recommendations()
    return render_template('recommendations.html',
                           first=top3[0],
                           second=top3[1],
                           third=top3[2])


@app.route("/dashboard")
def dashboard():
    """
    Send the plotly-encoded JSON string to the HTML template to be rendered.
    """
    plot = viz.plot_population("China")
    return render_template("viz.html", plot=plot)


if __name__ == "__main__":
    app.run(debug=True, port=5000)

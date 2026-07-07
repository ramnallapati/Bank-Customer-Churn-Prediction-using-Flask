from flask import Flask, render_template, request
import pandas as pd
import pickle

app = Flask(__name__)

# Load preprocessor
with open("preprocessor.pkl", "rb") as f:
    preprocessor = pickle.load(f)

# Load trained model
with open("best_model.pkl", "rb") as f:
    model = pickle.load(f)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():

    try:

        data = {
            "CreditScore": [float(request.form["CreditScore"])],
            "Geography": [request.form["Geography"]],
            "Gender": [request.form["Gender"]],
            "Age": [float(request.form["Age"])],
            "Tenure": [int(request.form["Tenure"])],
            "Balance": [float(request.form["Balance"])],
            "NumOfProducts": [int(request.form["NumOfProducts"])],
            "HasCrCard": [int(request.form["HasCrCard"])],
            "IsActiveMember": [int(request.form["IsActiveMember"])],
            "EstimatedSalary": [float(request.form["EstimatedSalary"])]
        }

        df = pd.DataFrame(data)

        # Transform
        transform_df = pd.DataFrame(
            preprocessor.transform(df),
            columns=preprocessor.get_feature_names_out()
        )

        # Drop the feature removed during training
        transform_df.drop(
            columns=["remainder__HasCrCard"],
            inplace=True
        )

        prediction = model.predict(transform_df)[0]
        probability = model.predict_proba(transform_df)[0][1]

        if prediction == 1:
            result = "⚠ Customer is likely to Churn"
            color = "danger"
        else:
            result = "✅ Customer is likely to Stay"
            color = "success"

        return render_template(
            "index.html",
            prediction=result,
            probability=f"{probability:.2%}",
            color=color
        )

    except Exception as e:
        return render_template(
            "index.html",
            prediction="Error",
            probability=str(e),
            color="warning"
        )


if __name__ == "__main__":
    app.run(debug=True)
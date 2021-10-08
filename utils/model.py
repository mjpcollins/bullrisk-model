from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
import pandas as pd


def run_model(df):
    threats = df[df['Risk Type'] == 'Threat']
    l = ['RiskID', 'Risk Status', 'Risk Category', 'Phase Impacted', 'Initial Likelihood']
    threats = threats[l]

    category_map = {f"Risk Category{i}": i for i in range(1, 25)}
    threats['Risk Category'] = threats['Risk Category'].map(category_map)

    status_map = {'Passed - Not Occurred': 1, 'Passed - Occurred': 2, 'Live - Not Occurred': 3, 'Live - Occurring': 4}
    threats['Risk Status'] = threats['Risk Status'].map(status_map)

    # replace 4 with 1 for the mL model
    threats['Risk Status'] = threats['Risk Status'].replace(4, 2)
    threats['Risk Status'] = threats['Risk Status'].replace(1, 0)
    threats['Risk Status'] = threats['Risk Status'].replace(2, 1)

    # remove missing values from a specific column
    threats = threats[(~threats['Phase Impacted'].isnull())]
    cat_phase = {'Implementation': 1, 'Definition': 2, 'Closeout': 3, 'IAP': 4, 'Handover': 5, 'Concept': 6}
    threats['Phase Impacted'] = threats['Phase Impacted'].map(cat_phase)

    threats = threats[threats['Initial Likelihood'] != 0]
    historic_threats = threats[threats['Risk Status'] != 3]
    historic_threats = historic_threats.dropna().reset_index(drop=True)

    # Balance the datasets so that 50% is 0 50% is 1
    historic_true = historic_threats[historic_threats['Risk Status'] == 1]
    historic_false = historic_threats[historic_threats['Risk Status'] == 0]
    historic_false_sample = historic_false.sample(n=len(historic_true))
    historic_training_data = pd.concat([historic_false_sample, historic_true]).reset_index(drop=True)

    model_features = ['Risk Category', 'Phase Impacted', 'Initial Likelihood']
    y = historic_training_data['Risk Status']
    X = historic_training_data[model_features]

    # instantiate the classifier
    logreg = LogisticRegression()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.4, random_state=42)
    logreg.fit(X_train, y_train)

    # estimating the possible occurrence of the future risks
    future_threats = threats[threats['Risk Status'] == 3]
    X_future = future_threats[model_features]
    future_threats['prediction'] = logreg.predict(X_future)
    future_threats['y_prediction_prob'] = logreg.predict_proba(X_future)[:, 1]
    future_threats.columns = [f'model_result_{col}' for col in future_threats.columns]
    all_data = df.set_index('RiskID').join(future_threats.set_index('model_result_RiskID'))

    # Uncomment if you wish to run metrics
    # y_pred_prob = logreg.predict_proba(X_test)[:, 1]
    # metrics(y_test, y_pred_prob)

    return all_data


def metrics(y_test, y_pred_prob):
    from matplotlib import pyplot as plt
    from sklearn.metrics import roc_curve
    fpr, tpr, thresholds = roc_curve(y_test, y_pred_prob)
    # Plot ROC curve
    plt.plot([0, 1], [0, 1], 'k--')
    # plt.plot([0, 10], [0, 10], 'k--')
    plt.plot(fpr, tpr)
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC Curve')
    plt.show()


if __name__ == '__main__':
    import_file = 'Risk.xlsx'
    file = import_file
    data = pd.ExcelFile(file)
    risk = data.parse(0, skiprows=0)
    out = run_model(risk)
    print()

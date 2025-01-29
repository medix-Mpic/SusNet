import xgboost as xgb
import pandas as pd
import numpy as np

def predict_from_dataframe(model_path, input_data , orig_data):
    """
    Load the XGBoost model and predict labels from a given dataframe.
    
    :param model_path: Path to the saved XGBoost model (.json or .bin file)
    :param input_data: Preprocessed pandas DataFrame (numeric features only)
    :return: Predicted labels (numpy array)
    """
    # Load the trained model
    model = xgb.Booster()
    model.load_model(model_path)
    
    # Convert DataFrame to XGBoost DMatrix
    dinput = xgb.DMatrix(input_data)
    
    # Make predictions
    predictions = model.predict(dinput)
    
    # Convert probabilities to binary labels (0 or 1)
    predicted_labels = np.where(predictions >= 0.5, 1, 0)
    
    # Add predictions as a new column
    orig_data["prediction"] = np.where(predicted_labels == 1, "sus", "safe")
    
    # Reorder columns to make 'prediction' the first column
    columns = ['prediction'] + [col for col in orig_data.columns if col != 'prediction']
    orig_data = orig_data[columns]
<<<<<<< HEAD
    
    # Exclude 'sus' and 'evil' columns if they exist
    columns_to_exclude = ['sus', 'evil']
    orig_data = orig_data.loc[:, ~orig_data.columns.isin(columns_to_exclude)]
=======
>>>>>>> ae4ca2225ab7218f1ed3ba25d4a51d8c90742844
        
    return orig_data
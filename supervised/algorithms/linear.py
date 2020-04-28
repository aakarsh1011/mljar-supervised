import logging
import os
import sklearn
import pandas as pd 
import numpy as np
from sklearn.linear_model import LogisticRegression, LinearRegression

from supervised.algorithms.algorithm import BaseAlgorithm
from supervised.algorithms.sklearn import SklearnAlgorithm
from supervised.algorithms.registry import AlgorithmsRegistry
from supervised.algorithms.registry import BINARY_CLASSIFICATION
from supervised.algorithms.registry import MULTICLASS_CLASSIFICATION
from supervised.algorithms.registry import REGRESSION
from supervised.utils.config import LOG_LEVEL

logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)


class LinearAlgorithm(SklearnAlgorithm):

    algorithm_name = "Logistic Regression"
    algorithm_short_name = "Linear"

    def __init__(self, params):
        super(LinearAlgorithm, self).__init__(params)
        logger.debug("LinearAlgorithm.__init__")
        self.max_iters = 1
        self.library_version = sklearn.__version__
        self.model = LogisticRegression(n_jobs=-1)

    def file_extension(self):
        return "linear"
    
    def interpret(
        self,
        X_train,
        y_train,
        X_validation,
        y_validation,
        model_file_path,
        learner_name,
        target_name=None,
        class_names=None,
        metric_name=None,
        ml_task=None,
    ):
        super(LinearAlgorithm, self).interpret(
            X_train,
            y_train,
            X_validation,
            y_validation,
            model_file_path,
            learner_name,
            target_name,
            class_names,
            metric_name,
            ml_task,
        )
        if X_train.shape[1] > 100:
            # if too many columns, skip this step
            return
        coefs = self.model.coef_
        intercept = self.model.intercept_
        if self.params["ml_task"] == BINARY_CLASSIFICATION:
            df = pd.DataFrame(
                {
                    "feature": ["intercept"] + X_train.columns.tolist(),
                    "weight": [intercept[0]] + list(coefs[0,:]),
                }
            )
            df.to_csv(
                os.path.join(model_file_path, f"{learner_name}_coefs.csv"), index=False
            )
        elif self.params["ml_task"] == MULTICLASS_CLASSIFICATION:
            classes = list(class_names)
            if isinstance(class_names, dict):
                classes = class_names.values()
            if len(classes) > 20:
                # if there are too many classes, skip this step
                return
            df = pd.DataFrame(
                np.transpose(np.column_stack((intercept, coefs))),
                index=["intercept"] + X_train.columns.tolist(),
                columns=classes
            )
            df.to_csv(
                os.path.join(model_file_path, f"{learner_name}_coefs.csv"), index=True
            )


class LinearRegressorAlgorithm(SklearnAlgorithm):

    algorithm_name = "Linear Regression"
    algorithm_short_name = "Linear"

    def __init__(self, params):
        super(LinearRegressorAlgorithm, self).__init__(params)
        logger.debug("LinearRegressorAlgorithm.__init__")
        self.max_iters = 1
        self.library_version = sklearn.__version__
        self.model = LinearRegression(n_jobs=-1)

    def file_extension(self):
        return "linear"

    def interpret(
        self,
        X_train,
        y_train,
        X_validation,
        y_validation,
        model_file_path,
        learner_name,
        target_name=None,
        class_names=None,
        metric_name=None,
        ml_task=None,
    ):
        super(LinearRegressorAlgorithm, self).interpret(
            X_train,
            y_train,
            X_validation,
            y_validation,
            model_file_path,
            learner_name,
            target_name,
            class_names,
            metric_name,
            ml_task,
        )
        if X_train.shape[1] > 100:
            # if too many columns, skip this step
            return
        coefs = self.model.coef_
        intercept = self.model.intercept_
        df = pd.DataFrame(
            {
                "feature": ["intercept"] + X_train.columns.tolist(),
                "weight": [intercept] + list(coefs),
            }
        )
        df.to_csv(
            os.path.join(model_file_path, f"{learner_name}_coefs.csv"), index=False
        )


additional = {"max_steps": 1, "max_rows_limit": None, "max_cols_limit": None}
required_preprocessing = [
    "missing_values_inputation",
    "convert_categorical",
    "scale",
    "target_as_integer",
]

AlgorithmsRegistry.add(
    BINARY_CLASSIFICATION, LinearAlgorithm, {}, required_preprocessing, additional
)
AlgorithmsRegistry.add(
    MULTICLASS_CLASSIFICATION, LinearAlgorithm, {}, required_preprocessing, additional
)

regression_required_preprocessing = [
    "missing_values_inputation",
    "convert_categorical",
    "scale",
    "target_scale",
]

AlgorithmsRegistry.add(
    REGRESSION, LinearRegressorAlgorithm, {}, regression_required_preprocessing, additional
)

import os
import numpy as np

# prefer lightweight tflite-runtime instead of full TensorFlow
try:
    from tflite_runtime.interpreter import Interpreter
except ImportError:
    # fall back to TensorFlow if tflite-runtime isn't installed
    import tensorflow as tf
    Interpreter = tf.lite.Interpreter


class KeyPointClassifier(object):
    def __init__(
        self,
        model_path: str = 'model/keypoint_classifier/keypoint_classifier.tflite',
        num_threads: int = 1,
    ):
        # try opening the provided path as-is first (relative to cwd)
        if not os.path.isabs(model_path):
            candidate = os.path.abspath(model_path)
            if os.path.exists(candidate):
                model_path = candidate
            else:
                # fall back to locations relative to this source file
                base = os.path.dirname(os.path.abspath(__file__))
                # same directory as this file
                local = os.path.join(base, os.path.basename(model_path))
                if os.path.exists(local):
                    model_path = local
                else:
                    # maybe the user kept the original relative pattern from
                    # the project root; try from two levels up
                    root = os.path.abspath(os.path.join(base, os.pardir, os.pardir))
                    root_candidate = os.path.join(root, model_path)
                    if os.path.exists(root_candidate):
                        model_path = root_candidate
        # final sanity check
        if not os.path.exists(model_path):
            raise ValueError(f"Could not locate keypoint classifier model at {model_path}")
        self.interpreter = Interpreter(model_path=model_path,
                                       num_threads=num_threads)

        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

    def __call__(
        self,
        landmark_list,
    ):
        input_details_tensor_index = self.input_details[0]['index']
        self.interpreter.set_tensor(
            input_details_tensor_index,
            np.array([landmark_list], dtype=np.float32))
        self.interpreter.invoke()

        output_details_tensor_index = self.output_details[0]['index']

        result = self.interpreter.get_tensor(output_details_tensor_index)

        result_index = np.argmax(np.squeeze(result))

        return result_index

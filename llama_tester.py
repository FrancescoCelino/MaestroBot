# https://github.com/openlm-research/open_llama
# https://pypi.org/project/transformers/
# https://github.com/abetlen/llama-cpp-python

from transformers import pipeline
# generator = pipeline("text-generation", model="gpt2")
# print(generator("Hello, I'm a language model,", max_length=30, num_return_sequences=1))
import tensorflow as tf
print("TensorFlow version:", tf.__version__)
print("GPU Available: ", tf.config.list_physical_devices('GPU'))
from tensorflow.python.client import device_lib
print(device_lib.list_local_devices())

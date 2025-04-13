# https://github.com/openlm-research/open_llama
# https://pypi.org/project/transformers/
# https://github.com/abetlen/llama-cpp-python

from transformers import pipeline
# generator = pipeline("text-generation", model="gpt2")
# print(generator("Hello, I'm a language model,", max_length=30, num_return_sequences=1))
import tensorflow as tf
print("GPUs:", tf.config.list_physical_devices('GPU'))
print("Built with CUDA:", tf.sysconfig.get_build_info()["cuda_version"])
print("Built with cuDNN:", tf.sysconfig.get_build_info()["cudnn_version"])

"""
Example

secret = SecretData(data_loader.load_file_as_binary('TestImage/girl128bw.png'), complexityThreshold=0.3)
host = HostImageColor(host_path='TestImage/girl512color.png', complexity_threshold=0.3)
encoder = Encoder(host_image=host, complexity_threshold=0.3, secret_data=secret, file_name='a.png')
new_host = encoder.encode()
new_host.write_image_to("TestImage/hidden/test.png")


decoder = Decoder('TestImage/hidden/test.png', complexity_threshold=0.3, black_white=False)
decoder.decode()
"""
import time

from classes.decoder import Decoder
from classes.encoder import Encoder
from classes.image.host_image_color import HostImageColor
from classes.secret_data import SecretData
from misc import data_loader

threshold = 0.45
encode_start = time.perf_counter()
secret = SecretData(data_loader.load_file_as_binary('demo/shakespeare.txt'), complexityThreshold=threshold)

host = HostImageColor(host_path='demo/mountains.jpg', complexity_threshold=threshold)
usable_blocks = sum(layer.writable_blocks_count for layer in host.writing_layers(3)) - 6  # 6 blocks hold the file name and length
print(f"Embedding capacity: {usable_blocks} blocks = {usable_blocks * 63 // 8} bytes")
encoder = Encoder(host_image=host, complexity_threshold=threshold, secret_data=secret, file_name="shakespeare.txt")
encoded = encoder.encode()
encoded.write_image_to('demo/mountains_hidden.png')
encode_time = time.perf_counter() - encode_start

decode_start = time.perf_counter()
decoder = Decoder(source_file_path='demo/mountains_hidden.png', complexity_threshold=threshold, black_white=False)
decoder.decode()
decode_time = time.perf_counter() - decode_start

print("\nDemo stats:")
print(f"Available blocks : {usable_blocks}")
print(f"Blocks used      : {secret.number_of_blocks} ({100 * secret.number_of_blocks / usable_blocks:.2f}%)")
print(f"Encoding time    : {encode_time:.2f}s")
print(f"Decoding time    : {decode_time:.2f}s")

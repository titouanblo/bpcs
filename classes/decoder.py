import os

from PIL import Image

from classes.bitplane.BitPlane64 import Bitplane64
from classes.image.host_image_bw import HostImageBW
from classes.image.host_image_color import HostImageColor
from classes.image.image_protocol import HostImage


class Decoder:
    image : HostImage
    data_length : int
    nb_file_name_block : int = 5
    def __init__(self, source_file_path : str, complexity_threshold : float, black_white : bool):
        image: Image.Image = Image.open(source_file_path).convert('RGB')
        if black_white:
            self.image = HostImageBW(source_file_path, complexity_threshold)
        else:
            self.image = HostImageColor(source_file_path, complexity_threshold)

    def _get_hidden_metadata(self) -> (str, int):
        """
        Gets the filename and the number of blocks coded into the image.
        :return:
        """
        file_name_bin = ""
        data_length = ""
        meta_decoded_counter = 0
        for layer in self.image.writing_layers(3):
            for block_ind in layer.writable_blocks_map:
                block = layer.blocks[block_ind]
                if block.bitlist[63] == "1":
                    # Block was conjugated.
                    block = block.conjugate()
                if meta_decoded_counter < 5:
                    file_name_bin += bin((block.bitplane >> 1))[2:].zfill(63)
                elif meta_decoded_counter == 5:
                    data_length = block.bitplane >> 1
                    print(data_length)

                meta_decoded_counter += 1
                if meta_decoded_counter == 6:
                    break
            if meta_decoded_counter == 6:
                break

        file_name = int(file_name_bin, 2).to_bytes(length=5*64, byteorder="big",
                                                               signed=False).decode().replace("\x00", "")
        return file_name, data_length


    def decode(self):
        file_name, self.data_length = self._get_hidden_metadata()
        data_fetched_counter = -1 - self.nb_file_name_block # Those blocks have already been read.
        whole_data = ''
        finish = False
        for layer in self.image.writing_layers(3):
            for wblock_ind in layer.writable_blocks_map:

                if data_fetched_counter >= 0:
                    block = layer.blocks[wblock_ind]
                    bitstring = ""
                    if block.bitlist[63] == "1":
                        bitstring = block.conjugate().bitstring[0:63]
                    else:
                        bitstring = block.bitstring[:63]
                    whole_data += bitstring



                data_fetched_counter += 1
                if self.data_length <= len(whole_data):
                    finish = True
                    break
            if finish: break

        whole_data = whole_data[:self.data_length]
        print("out : ", whole_data)
        os.makedirs('decoded', exist_ok=True)
        newfile = open(f'decoded/{file_name}', 'wb')
        print(int(whole_data, 2).to_bytes(length=int(self.data_length/8 + 1), byteorder="big", signed=False).strip(b'\x00'))
        newfile.write(int(whole_data, 2).to_bytes(length=int(self.data_length/8 + 1), byteorder="big", signed=False).strip(b'\x00'))
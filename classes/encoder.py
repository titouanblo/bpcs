from classes.bitplane.BitPlane64 import BitplaneOverflow
from classes.bitplane.BitPlane64ConjugateBit import Bitplane64ConjugateBit
from classes.image.host_image_bw import HostImageBW
from classes.image.image_protocol import HostImage
from classes.secret_data import SecretData


class Encoder:
    """
    Encodes the secret data into the host image.

    Before encoding the data, two blocks are placed, the first one corresponds to the name of the file. The second one
    is the binary length of the data stored in the image.
    """

    block_to_hide : int
    nb_block_for_file_name = 5

    def __init__(self, host_image : HostImage, secret_data : SecretData, file_name : str, complexity_threshold : float):
        """
        :param host_image:
        :param secret_data:
        :param file_name: 10 chars max
        """
        if complexity_threshold >= 0.5:
            raise Exception ("Can't have more complexity than 0.5")

        file_name_bin = str(bin(int.from_bytes(bytearray(str.encode(file_name)), 'big'))[2:])
        if len(file_name_bin) > self.nb_block_for_file_name * 63:
            print(bin(int.from_bytes(bytearray(str.encode(file_name)), 'big')))
            print(len(bin(int.from_bytes(bytearray(str.encode(file_name)), 'big'))))
            raise Exception("file_name length is too long, cannot store it in one bitplane.")

        file_name_bin = file_name_bin.rjust(self.nb_block_for_file_name*63, '0')
        self.file_name_blocks = []
        for i in range(self.nb_block_for_file_name):
            block = Bitplane64ConjugateBit(int(file_name_bin[i*63:i*63+63], 2))
            if block.complexity < complexity_threshold:
                block = -block
            self.file_name_blocks.append(block)

        self.length_block = Bitplane64ConjugateBit(secret_data.data_length)
        print(secret_data.data_length)
        if self.length_block.complexity < complexity_threshold:
            self.length_block = -self.length_block

        self.host_image = host_image
        self.secret_data = secret_data

        self.block_to_hide = self.secret_data.number_of_blocks + 1 + self.nb_block_for_file_name
        available_blocks = sum(layer.writable_blocks_count for layer in self.host_image.writing_layers(bellow=3))  # Only the layers encode() writes to.
        if available_blocks < self.block_to_hide:
            raise Exception(f"Not enough storage in the host image, available : {available_blocks}, needed : {self.block_to_hide}")

    def encode(self):
        data_written_counter = 0
        finish = False
        total_encoded = ""
        for layer in self.host_image.writing_layers(bellow=3):
            print(f"Hiding data blocks, {self.block_to_hide - data_written_counter} to go !")
            for wblock_ind in layer.writable_blocks_map:
                if data_written_counter < 5:
                    layer.blocks[wblock_ind] = self.file_name_blocks[data_written_counter]
                elif data_written_counter == 5:
                    layer.blocks[wblock_ind] = self.length_block
                else:
                    layer.blocks[wblock_ind] = self.secret_data.blocks[data_written_counter - (self.nb_block_for_file_name + 1)]
                    total_encoded += self.secret_data.blocks[data_written_counter - (self.nb_block_for_file_name + 1)].bitstring[:63]
                    if data_written_counter >= self.block_to_hide-1:
                        finish = True
                        break

                data_written_counter += 1
            if finish:
                break
        print("Data is hidden !")
        return self.host_image
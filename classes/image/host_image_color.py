from PIL import Image
from matplotlib import pyplot as plt

from classes.bit_layer import BitLayer
from classes.image.host_image_bw import HostImageBW
from classes.image.image_protocol import HostImage



class HostImageColor(HostImage):
    """
    Represents an image with three distinct color channel (rgb).

    This class is creating three instances of HostImageBW, each with their corresponding color channel.
    """
    host_image_decomposition : [HostImageBW]
    side_length : int
    writable_blocks_count : int

    def __init__(self, host_path: str, complexity_threshold: float):
        self.host_image_decomposition = []
        for color in range(3):
            self.host_image_decomposition.append(HostImageBW(host_path, complexity_threshold, color))
        self.writable_blocks_count = sum([host.writable_blocks_count for host in self.host_image_decomposition])
        self.side_length = self.host_image_decomposition[0].side_length



    def show_original_image(self, show_plt = True):
        plt.figure()
        imdata = [
            [[int(host.pixel_values[line * host.side_length + column], 2) for host in self.host_image_decomposition] for column in range(self.side_length)]
            for line in range(self.side_length)]
        plt.imshow(imdata)
        if show_plt : plt.show()

    @property
    def _rgb_data(self) -> list[list[list[int]]]:
        bin_datas = [host.image_bin_data for host in self.host_image_decomposition]
        imdata = []
        for line in range(self.side_length):
            imdata.append([])
            for column in range(self.side_length):
                imdata[line].append([int(bin_datas[color][line * self.side_length + column], 2) for color in range(3)])
        return imdata


    def show_image(self, show_plt = True):
        plt.figure()
        plt.imshow(self._rgb_data)
        if show_plt : plt.show()

    def writing_layers(self, bellow : int):
        for layer_ind in range(7, bellow, -1):
            for color in range(3):
                yield self.host_image_decomposition[color].layers[layer_ind]

    def write_image_to(self, filepath : str):
        rgb = self._rgb_data
        img : Image.Image = Image.new('RGB', [self.side_length, self.side_length], 255)
        data = img.load()
        for line in range(img.size[0]):
            for column in range(img.size[1]):
                data[column, line] = tuple(rgb[line][column])
        img.save(filepath)

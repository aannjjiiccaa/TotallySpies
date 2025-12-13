import cv2
import numpy as np
from .base import StegAlgo


class EdgeLSBSteg(StegAlgo):
    def __init__(self, edge_threshold1=100, edge_threshold2=200):
        self.name = "Edge LSB"
        self.edge_threshold1 = edge_threshold1
        self.edge_threshold2 = edge_threshold2

    def getCapacity(self, image_path):
        image = cv2.imread(image_path)
        if image is None:
            raise FileNotFoundError("Image not found.")

        grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(grayscale, self.edge_threshold1, self.edge_threshold2)
        num_edge_pixels = np.count_nonzero(edges)
        return num_edge_pixels//8

    def capacity(self, image_path, secret_message):
        image = cv2.imread(image_path)
        if image is None:
            raise FileNotFoundError("Image not found.")

        grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(grayscale, self.edge_threshold1, self.edge_threshold2)
        num_edge_pixels = np.count_nonzero(edges)
        total_bits_needed = len(secret_message) * 8 + 32
        return num_edge_pixels >= total_bits_needed

    @StegAlgo.runtime
    def embed(self, image_path, secret_message, output_path=None):
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError("Image not found")

        grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(grayscale, self.edge_threshold1, self.edge_threshold2)

        message_bits = self.text_to_bits(secret_message)
        length_bits = f'{len(message_bits):032b}'
        full_message = length_bits + message_bits

        bit_index = 0
        height, width = edges.shape

        for y in range(height):
            for x in range(width):
                if edges[y, x] > 0:
                    if bit_index >= len(full_message):
                        break
                    pixel = image[y, x]
                    blue = int(pixel[0])
                    blue = (blue & ~1) | int(full_message[bit_index])
                    pixel[0] = np.uint8(blue)
                    image[y, x] = pixel
                    bit_index += 1
            if bit_index >= len(full_message):
                break

        if bit_index < len(full_message):
            raise ValueError("Message too long to embed in edge pixels.")

        if output_path:
            if not output_path.lower().endswith(".png"):
                output_path = output_path.rsplit(".", 1)[0] + ".png"
            cv2.imwrite(output_path, image)
            print(f"Message embedded and saved to {output_path}")
        return image

    @StegAlgo.runtime
    def extract(self, stego_image_path):
        image = cv2.imread(stego_image_path)
        if image is None:
            raise ValueError("Stego image not found")

        grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(grayscale, self.edge_threshold1, self.edge_threshold2)

        bits = ""
        height, width = edges.shape
        for y in range(height):
            for x in range(width):
                if edges[y, x] > 0:
                    bits += str(image[y, x][0] & 1)

        if len(bits) < 32:
            raise ValueError("Image does not contain enough data.")

        msg_length = int(bits[:32], 2)
        if len(bits) < 32 + msg_length:
            raise ValueError("Incomplete message extracted.")

        message_bits = bits[32:32 + msg_length]

        try:
            return self.bits_to_text(message_bits)
        except UnicodeDecodeError:
            raise ValueError("Failed to decode extracted message. Possibly corrupted or wrong image.")

import unittest
import os
from PIL import Image, ImageDraw
from img_to_svg.main import pixels2svg

class TestImageToSvg(unittest.TestCase):

    def setUp(self):
        self.input_file = 'test_input.png'
        self.output_file = 'test_output.svg'
        self.create_dummy_image(self.input_file, 100, 50, 'Test')

    def tearDown(self):
        if os.path.exists(self.input_file):
            os.remove(self.input_file)
        if os.path.exists(self.output_file):
            os.remove(self.output_file)

    def create_dummy_image(self, filename, width, height, text):
        img = Image.new('RGB', (width, height), color = 'blue')
        d = ImageDraw.Draw(img)
        d.text((10,10), text, fill=(255,255,0))
        img.save(filename)

    def test_conversion(self):
        pixels2svg(input_path=self.input_file, output_path=self.output_file)
        self.assertTrue(os.path.exists(self.output_file))
        with open(self.output_file, 'r') as f:
            content = f.read()
            self.assertTrue(content.startswith('<?xml version="1.0" encoding="utf-8" ?>'))
            self.assertTrue('<svg' in content)

if __name__ == '__main__':
    unittest.main()

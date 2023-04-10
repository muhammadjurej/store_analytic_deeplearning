import os

class Config:
      def __init__(self) -> None:
            self.ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
            self.sample_video_path = self.ROOT_DIR + "/data_sample/sample_1.mp4"
            self.db = self.ROOT_DIR + "/db/store_data.db"
            self.region_data_path = self.ROOT_DIR + "/config/store_region.txt"
            self.model_path = self.ROOT_DIR + "/model/ssd_mobilenet_v1_1_metadata_1.tflite"
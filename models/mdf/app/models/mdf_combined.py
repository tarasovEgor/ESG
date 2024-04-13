from app.dto import ModelType
from app.models.base_mdf import BaseMDF


class MDFCombined(BaseMDF):
    name = ModelType.mdf_combined
    file_path = "morality_with_v2.csv.zip"

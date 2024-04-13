from app.dto import ModelType
from app.models.base_mdf import BaseMDF


class MDFMortality(BaseMDF):
    name = ModelType.mdf_adjusted
    file_path = "morality.csv.zip"

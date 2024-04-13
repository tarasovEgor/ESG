import argparse

from app.dto import ModelType
from app.models.base_mdf import BaseMDF


def parse_args() -> BaseMDF:
    parser = argparse.ArgumentParser(description="CLI for banks")
    parser.add_argument(
        "--model",
        choices=[parser_type for parser_type in ModelType],
        required=True,
    )
    return _get_class(parser.parse_args())


def _get_class(args: argparse.Namespace) -> BaseMDF:
    match args.model:
        case ModelType.mdf:
            from app.models.mdf import MDF

            return MDF()
        case ModelType.mdf_adjusted:
            from app.models.mdf_mortality import MDFMortality

            return MDFMortality()
        case ModelType.mdf_combined:
            from app.models.mdf_combined import MDFCombined

            return MDFCombined()
        case _:
            raise ValueError("Unknown model type")

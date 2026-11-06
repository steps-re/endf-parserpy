"""Section filters with a tape header that has blank MF/MT columns.

With include= or exclude=, EndfParserCpp reads the tape header verbatim.
Its MF/MT columns used to go through std::stoi, which threw
ValueError("stoi") on a blank field, e.g. in the FENDL-3.2c files.
"""

from pathlib import Path
import pytest
from endf_parserpy import EndfParserCpp, EndfParserPy


TESTDATA = Path(__file__).parent / "testdata"


@pytest.fixture(scope="module")
def blank_header_text():
    lines = (TESTDATA / "n_2925_29-Cu-63.endf").read_text().splitlines()
    # MAT=0, with MF, MT and the line-number columns reduced to a final 0
    lines[0] = "FENDL-3.0".ljust(69) + "0" + " " * 9 + "0"
    return "\n".join(lines) + "\n"


@pytest.mark.parametrize("ParserCls", [EndfParserCpp, EndfParserPy])
@pytest.mark.parametrize(
    "kwargs", [{}, {"include": [(3, 1)]}, {"include": [3]}, {"exclude": [(3, 1)]}]
)
def test_blank_mfmt_in_tape_header(blank_header_text, ParserCls, kwargs):
    parser = ParserCls(ignore_missing_tpid=False)
    endf_dict = parser.parse(blank_header_text, **kwargs)
    if "include" in kwargs:
        assert 3 in endf_dict and 1 in endf_dict[3]
    if "exclude" in kwargs:
        # excluded sections are kept as verbatim lines instead of being parsed
        assert isinstance(endf_dict[3][1], list)

from ibis_profiling.report.structure.variables.render_categorical import render_categorical


def test_render_categorical():
    assert render_categorical({}) is not None

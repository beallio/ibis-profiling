from ibis_profiling.report.structure.variables.render_numeric import render_numeric


def test_render_numeric():
    assert render_numeric({}) is not None

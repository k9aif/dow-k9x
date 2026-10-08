# SPDX-License-Identifier: Apache-2.0
"""Word ICD: loop-agent results are nested, the file name carries the program, and each job's and
stage's file has its own storage key (JOB-20261008-66EB1F: 'unhashable type: slice'; Acquisition
stored ICD_unknown.docx; same-document jobs overwrote each other)."""

from k9_dow.reporting.section_mapper import SectionMapper
from k9_dow.utils.icd_composer import icd_metadata

VIEWS = "# DoDAF 2.0 View: OV-1 (Capability Context)\nOperational context ..."
# Shape of a K9ValidationLoopAgent result: the final agent's result is wrapped.
NESTED = {"agent": "DAS ViewGenerator", "disposition": "accepted",
          "output": {"agent": "DAS ViewGenerator", "view_type": "OV-1", "output": VIEWS},
          "iterations": 2, "final_confidence": 0.9}


def test_nested_loop_agent_output_is_extracted():
    assert SectionMapper._extract_text(NESTED) == VIEWS.strip()
    assert SectionMapper._extract_text({"output": "plain"}) == "plain"
    assert SectionMapper._extract_text({"output": 42}) == ""


def test_diagram_extraction_accepts_nested_views():
    specs = SectionMapper().extract_diagrams({"generated_views": NESTED})
    assert len(specs) == 1 and specs[0].source.startswith("# DoDAF 2.0 View: OV-1")


def test_views_reach_the_icd_tokens():
    tokens = SectionMapper().to_tokens({"generated_views": NESTED}, icd_metadata("F22.md", "J", "jcids"))
    assert any("OV-1 (Capability Context)" in v for v in tokens.values())


def test_icd_metadata_names_program_job_and_stage():
    m = icd_metadata("SENTINEL_Cyber_Defense.md", "JOB-1", "acquisition")
    assert m["program_name"] == "SENTINEL Cyber Defense"
    assert (m["job_id"], m["stage"]) == ("JOB-1", "acquisition")


def test_each_job_and_stage_gets_its_own_storage_key(monkeypatch):
    from k9_dow.reporting import icd_report_builder as mod
    uploaded = []

    class Store:
        def upload(self, bucket, key, data, meta=None):
            uploaded.append(key)
            return f"s3://{bucket}/{key}"

    import k9_aif_abb.k9_factories.object_storage_factory as osf
    monkeypatch.setattr(osf.ObjectStorageFactory, "create", staticmethod(lambda cfg: Store()))
    builder = mod.IcdReportBuilder(config={})
    monkeypatch.setattr(builder, "build", lambda prior, meta: b"docx")
    for job, stage in (("JOB-1", "jcids"), ("JOB-2", "jcids"), ("JOB-1", "acquisition")):
        builder.build_and_store({}, icd_metadata("F22_Maintenance.md", job, stage), {})
    assert len(set(uploaded)) == 3
    assert uploaded[0] == "icd/JOB-1/jcids/ICD_f22_maintenance.docx"

import copy
import io
import json
import urllib.error
from unittest.mock import Mock

import pytest

import echo_local_analysis as local


FILES = [{"name": "example.log", "text": "Startup\nERROR: failed login\nReady"}]
MODEL = "qwen2.5:3b"
DETAILS = {"model_info": {"general.architecture": "qwen2", "qwen2.context_length": 32768},
           "capabilities": ["completion"]}
REPORT = {"summary": "Review the failed login.", "findings": [
    {"file": "example.log", "line": 2, "evidence": "ERROR: failed login",
     "explanation": "A login failed.", "next_step": "Review the relevant login settings."},
]}


@pytest.fixture()
def transport(monkeypatch):
    def response(endpoint, payload=None, timeout=5):
        if endpoint == "tags":
            return {"models": [{"name": MODEL, "size": 123}]}
        if endpoint == "show":
            return copy.deepcopy(DETAILS)
        if endpoint == "chat":
            return {"done": True, "done_reason": "stop", "message": {"content": json.dumps(REPORT)}}
        pytest.fail("Unexpected operation")
    mock = Mock(side_effect=response)
    monkeypatch.setattr(local, "local_request", mock)
    return mock


def test_read_only_local_analysis_has_verified_sources_and_no_tools(transport):
    result = local.analyze(FILES, MODEL, True, dutch=True)
    assert result["findings"] == REPORT["findings"]
    assert result["files"] == ["example.log"]
    assert [call.args[0] for call in transport.call_args_list] == ["tags", "show", "chat"]
    payload = transport.call_args_list[-1].args[1]
    assert payload["stream"] is False
    assert "tools" not in payload and "Dutch" in payload["messages"][0]["content"]
    assert "2: ERROR: failed login" in payload["messages"][1]["content"]
    assert FILES == [{"name": "example.log", "text": "Startup\nERROR: failed login\nReady"}]


@pytest.mark.parametrize("authorized", [False, 1, None, "true"])
def test_consent_before_any_model_or_content_request(transport, authorized):
    with pytest.raises(local.AnalysisError):
        local.analyze(FILES, MODEL, authorized)
    transport.assert_not_called()


@pytest.mark.parametrize("files", [
    [], FILES * 6, [{"name": "binary.txt", "text": "\x00x"}],
    [{"name": ".env", "text": "key"}], [{"name": "private_key.json", "text": "{}"}],
    [{"name": "..\\example.log", "text": "x"}], [{"name": "x.exe", "text": "x"}],
    [{"name": "empty.log", "text": " "}], [{"name": "x.log", "text": 1}],
    [{"name": "example.log", "text": "x"}, {"name": "EXAMPLE.LOG", "text": "y"}],
    [{"name": "x.log", "text": "x" * 12001}],
    [{"name": "x.log", "text": "\ud800"}],
])
def test_invalid_files_never_reach_ollama(transport, files):
    with pytest.raises(local.AnalysisError):
        local.analyze(files, MODEL, True)
    transport.assert_not_called()


@pytest.mark.parametrize("model", ["gemma:cloud", "alias-cloud", "--help", "x\npull", None, [], ""])
def test_bad_or_cloud_model_never_receives_content(transport, model):
    with pytest.raises(local.AnalysisError):
        local.analyze(FILES, model, True)
    transport.assert_not_called()


@pytest.mark.parametrize("details", [
    {**DETAILS, "remote_host": "https://ollama.com"},
    {**DETAILS, "remote_model": "remote"},
    {"capabilities": ["completion"]},
    {**DETAILS, "capabilities": ["embedding"]},
    {**DETAILS, "capabilities": None},
    {**DETAILS, "model_info": {"general.architecture": "qwen2", "qwen2.context_length": 4096}},
])
def test_remote_unknown_or_small_context_models_refused_before_content(transport, details):
    transport.side_effect = [{"models": [{"name": MODEL, "size": 123}]}, details]
    with pytest.raises(local.AnalysisError):
        local.analyze(FILES, MODEL, True)
    assert [call.args[0] for call in transport.call_args_list] == ["tags", "show"]


def test_uninstalled_model_is_not_pulled(transport):
    transport.side_effect = [{"models": []}]
    with pytest.raises(local.AnalysisError, match="not installed"):
        local.analyze(FILES, MODEL, True)
    assert transport.call_count == 1


def test_excessive_line_numbering_is_not_silently_truncated(transport):
    with pytest.raises(local.AnalysisError, match="Too many lines"):
        local.analyze([{"name": "x.log", "text": "\n" * 11000 + "end"}], MODEL, True)
    assert transport.call_count == 2


def test_exact_character_limit_is_accepted_but_combined_limit_is_enforced():
    files = [{"name": "first.log", "text": "x" * 6000}, {"name": "second.log", "text": "y" * 6000}]
    assert local.validate_files(files) == files
    with pytest.raises(local.AnalysisError) as error:
        local.validate_files(files + [{"name": "third.log", "text": "z"}])
    assert error.value.status == 413


def test_no_findings_is_a_completed_report_not_a_safety_guarantee(transport):
    transport.side_effect = [
        {"models": [{"name": MODEL, "size": 123}]}, DETAILS,
        {"done": True, "done_reason": "stop", "message": {"content": '{"summary":"No findings in this excerpt.","findings":[]}'}},
    ]
    assert local.analyze(FILES, MODEL, True)["findings"] == []


@pytest.mark.parametrize("mutation", ["file", "line", "boolean_line", "evidence", "extra", "summary"])
def test_model_hallucinated_evidence_or_invalid_structure_is_rejected(transport, mutation):
    report = copy.deepcopy(REPORT)
    if mutation == "boolean_line":
        report["findings"][0]["line"] = True
    elif mutation in {"file", "line", "evidence"}:
        report["findings"][0][mutation] = {"file": "other.log", "line": 99, "evidence": "invented"}[mutation]
    elif mutation == "extra":
        report["findings"][0]["command"] = "run this"
    else:
        report["summary"] = []
    transport.side_effect = [
        {"models": [{"name": MODEL, "size": 123}]}, DETAILS,
        {"done": True, "done_reason": "stop", "message": {"content": json.dumps(report)}},
    ]
    with pytest.raises(local.AnalysisError, match="unverified"):
        local.analyze(FILES, MODEL, True)


@pytest.mark.parametrize("response", [
    {"done": True, "done_reason": "length"}, {"done": False},
    {"done": True, "done_reason": "stop", "message": {"content": "not json"}},
    {"done": True, "done_reason": "stop", "message": None},
])
def test_incomplete_or_invalid_model_response_is_explicit(transport, response):
    transport.side_effect = [{"models": [{"name": MODEL, "size": 123}]}, DETAILS, response]
    with pytest.raises(local.AnalysisError):
        local.analyze(FILES, MODEL, True)
    assert not local.ANALYSIS_LOCK.locked()


def test_analysis_busy_does_not_send_another_file(transport):
    with local.ANALYSIS_LOCK:
        with pytest.raises(local.AnalysisError) as error:
            local.analyze(FILES, MODEL, True)
    assert error.value.status == 409
    transport.assert_not_called()


def test_transport_uses_only_fixed_loopback_no_proxy_or_redirect(monkeypatch):
    raw = json.dumps({"models": []}).encode()
    opener = Mock()
    opener.open.return_value = io.BytesIO(raw)
    factory = Mock(return_value=opener)
    monkeypatch.setattr(local.urllib.request, "build_opener", factory)
    assert local.local_request("tags") == {"models": []}
    handlers = factory.call_args.args
    assert handlers[0].proxies == {}
    assert isinstance(handlers[1], local.NoRedirect)
    assert handlers[1].redirect_request(None, None, 302, "", {}, "https://outside.example") is None
    request = opener.open.call_args.args[0]
    assert request.full_url == "http://127.0.0.1:11434/api/tags"
    assert not request.has_header("Authorization")
    with pytest.raises(ValueError):
        local.local_request("pull")


@pytest.mark.parametrize("failure", [
    urllib.error.URLError("offline"), TimeoutError(),
    urllib.error.HTTPError("http://127.0.0.1:11434", 302, "redirect", {}, None),
])
def test_transport_failure_has_no_fallback(monkeypatch, failure):
    opener = Mock()
    opener.open.side_effect = failure
    factory = Mock(return_value=opener)
    monkeypatch.setattr(local.urllib.request, "build_opener", factory)
    with pytest.raises(local.AnalysisError):
        local.local_request("chat", {"private": "synthetic"})
    assert opener.open.call_count == 1 and factory.call_count == 1

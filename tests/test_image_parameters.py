"""Native tool regressions for image edits and model resolution compatibility."""

import json
from pathlib import Path

import dify_plugin  # noqa: F401
import pytest
import requests
import yaml
from dify_plugin.config.config import DifyPluginEnv
from dify_plugin.core.plugin_registration import PluginRegistration
from dify_plugin.entities.tool import ToolRuntime


@pytest.fixture(scope="module")
def registration():
    return PluginRegistration(DifyPluginEnv())


def invoke_image(monkeypatch, registration, operation, parameters, *, ui_defaults=True):
    definition = yaml.safe_load(Path(f"tools/nano_banana_{operation}.yaml").read_text())
    inputs = (
        {p["name"]: p["default"] for p in definition["parameters"] if "default" in p}
        if ui_defaults
        else {}
    )
    inputs.update({"prompt": "Offline image fixture"})
    if operation == "edit":
        inputs["image_urls"] = '["https://example.com/portrait.png"]'
    inputs.update(parameters)
    original_inputs = dict(inputs)
    calls = []

    def send(method, url, **kwargs):
        prepared = requests.Request(
            method, url, json=kwargs.get("json"), headers=kwargs.get("headers")
        ).prepare()
        assert prepared.method == "POST"
        assert prepared.url == "https://api.acedata.cloud/nano-banana/images"
        calls.append(json.loads(prepared.body))
        result = requests.Response()
        result.status_code = 200
        result._content = b'{"task_id":"offline-fixture","status":"pending"}'
        result.close = lambda: None
        return result

    monkeypatch.setattr(requests, "request", send)
    cls = registration.get_tool_cls("nano-banana", definition["identity"]["name"])
    tool = cls(
        ToolRuntime(credentials={"acedata_bearer_token": "fixture"}, user_id=None, session_id=None),
        None,
    )
    try:
        list(tool._invoke(inputs))
    except ValueError:
        assert not calls
        assert inputs == original_inputs
        raise
    assert len(calls) == 1
    assert inputs == original_inputs
    assert calls[0]["action"] == operation
    return calls[0]


@pytest.mark.parametrize("ui_defaults", [False, True])
@pytest.mark.parametrize("parameters", [{}, {"aspect_ratio": None}, {"aspect_ratio": ""}])
def test_edit_omits_unspecified_ratio(monkeypatch, registration, ui_defaults, parameters):
    body = invoke_image(monkeypatch, registration, "edit", parameters, ui_defaults=ui_defaults)
    assert "aspect_ratio" not in body
    assert body["model"] == "nano-banana-2-lite"
    assert body["resolution"] == "1K"


@pytest.mark.parametrize("ratio", ["1:1", "3:2", "2:3", "16:9", "9:16", "4:3", "3:4"])
def test_edit_keeps_explicit_workflow_ratio(monkeypatch, registration, ratio):
    body = invoke_image(monkeypatch, registration, "edit", {"aspect_ratio": ratio})
    assert body["aspect_ratio"] == ratio


def test_generation_defaults_are_unchanged(monkeypatch, registration):
    body = invoke_image(monkeypatch, registration, "generate", {})
    assert body == {
        "action": "generate",
        "model": "nano-banana-2-lite",
        "prompt": "Offline image fixture",
        "count": 1,
        "aspect_ratio": "1:1",
        "resolution": "1K",
        "async": True,
    }


@pytest.mark.parametrize("operation", ["generate", "edit"])
@pytest.mark.parametrize(
    "model",
    ["nano-banana", "nano-banana:official", "nano-banana-2-lite", "nano-banana-2-lite:official"],
)
@pytest.mark.parametrize("resolution", ["1K", "2K", "4K"])
def test_1k_models_and_official_variants(monkeypatch, registration, operation, model, resolution):
    parameters = {"model": model, "resolution": resolution}
    if resolution != "1K":
        with pytest.raises(ValueError, match="supports 1K only"):
            invoke_image(monkeypatch, registration, operation, parameters)
    else:
        body = invoke_image(monkeypatch, registration, operation, parameters)
        assert body["model"] == model
        assert body["resolution"] == resolution


@pytest.mark.parametrize("operation", ["generate", "edit"])
@pytest.mark.parametrize("model", [None, ""])
def test_default_model_cannot_bypass_resolution_guard(monkeypatch, registration, operation, model):
    with pytest.raises(ValueError, match="supports 1K only"):
        invoke_image(monkeypatch, registration, operation, {"model": model, "resolution": "4K"})


@pytest.mark.parametrize("operation", ["generate", "edit"])
@pytest.mark.parametrize("resolution", ["1K", "2K", "4K"])
def test_2_1_keeps_every_resolution(monkeypatch, registration, operation, resolution):
    body = invoke_image(
        monkeypatch, registration, operation, {"model": "nano-banana-2.1", "resolution": resolution}
    )
    assert body["model"] == "nano-banana-2.1"
    assert body["resolution"] == resolution


@pytest.mark.parametrize("operation", ["generate", "edit"])
@pytest.mark.parametrize(
    "model",
    ["nano-banana-2", "nano-banana-2:official", "nano-banana-pro", "nano-banana-pro:official"],
)
def test_other_high_resolution_models_are_preserved(monkeypatch, registration, operation, model):
    body = invoke_image(monkeypatch, registration, operation, {"model": model, "resolution": "4K"})
    assert body["model"] == model
    assert body["resolution"] == "4K"

"""Formal output identity and expected Workflow form; never infer form from omissions."""
from pathlib import Path
from html.parser import HTMLParser
import re

from .audit_models import Finding


def audit_artifact_identity(path, html, canvas_type, instance, variant, policy, index=False):
    if policy not in ("current", "legacy"):
        return [Finding("ARTIFACT_POLICY", "unknown artifact policy")]
    if policy == "legacy" or html.body_attrs.get("data-mode") == "draft":
        return []
    attrs = html.body_attrs
    page = attrs.get("data-page-type")
    version = str(attrs.get("data-version", "")).removeprefix("v")
    slug = attrs.get("data-instance")
    findings = []
    if index:
        expected = f"{canvas_type}-canvas.html"
    elif canvas_type == "mvl" and page == "global":
        if variant not in ("noflow", "workflow"):
            findings.append(Finding("WORKFLOW_VARIANT", "current global requires --workflow-variant noflow|workflow"))
        if slug or instance or attrs.get("data-generation-path") == "transcript-direct":
            if not instance or slug != instance:
                findings.append(Finding("ARTIFACT_IDENTITY", "MAAU requires matching --instance and data-instance"))
            expected = f"maau-global-canvas-{slug}--{variant}-v{version}.html"
        else:
            expected = "maau-global-canvas.html" if variant == "noflow" else "maau-global-canvas--workflow.html"
    elif canvas_type == "mvl" and page == "module-detail":
        module = attrs.get("data-module", "")
        if not re.fullmatch(r"M[1-6]", module):
            findings.append(Finding("ARTIFACT_IDENTITY", "invalid module identity"))
        expected = f"module-{module.removeprefix('M')}-canvas--v{version}.html"
    else:
        if not instance or slug != instance:
            findings.append(Finding("ARTIFACT_IDENTITY", "current instance requires matching --instance and data-instance"))
        expected = f"{canvas_type}-canvas-{slug}--v{version}.html"
    if slug and not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
        findings.append(Finding("ARTIFACT_IDENTITY", "invalid instance slug"))
    if Path(path).name != expected:
        findings.append(Finding("ARTIFACT_IDENTITY", f"target {Path(path).name!r} must be {expected!r}"))
    return findings


class WorkflowSignature(HTMLParser):
    def __init__(self):
        super().__init__()
        self.classes = set()
        self.ids = set()
        self.svg = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = set((attrs.get("class") or "").split())
        self.classes.update(classes)
        self.ids.add(attrs.get("id"))
        self.svg |= tag == "svg" and "bpmn-flow" in classes


def audit_workflow_variant(source, data, variant, policy):
    dom = WorkflowSignature()
    dom.feed(source)
    if policy == "legacy":
        variant = "workflow"
    if variant == "noflow":
        if "workflow" in data or "workflow-flow" in dom.ids or any(c.startswith("bpmn-") for c in dom.classes):
            return [Finding("WORKFLOW_VARIANT", "noflow forbids workflow topology and BPMN DOM")]
    elif variant == "workflow":
        if not dom.svg or not {"bpmn-flow-wrap", "bpmn-legend", "bpmn-track", "bpmn-node"} <= dom.classes:
            return [Finding("WORKFLOW_VARIANT", "workflow requires SVG, wrapper, legend, tracks and nodes")]
    return []

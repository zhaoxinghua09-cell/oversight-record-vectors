#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
L1 - identifier normalisation, three routes: serial (sNNN) / content hash (sha256:) / produced-at timestamp (ISO)

Two modes:
  declared  : trust a declared alias table. The table is jointly maintained and can be wrong or poisoned.
  content   : trust only a hash recomputed from the version content. The declared table does not apply; anything that cannot be recomputed is unverifiable.

The inherent weakness of the timestamp route: it is single-valued only when produced_at is unique. Collisions are detected explicitly here.
"""
import hashlib
import json


def canonical_content(version):
    return json.dumps(version["content"], sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def content_hash(version):
    return "sha256:" + hashlib.sha256(canonical_content(version).encode("utf-8")).hexdigest()


class Normalizer:
    def __init__(self, revision, mode="content"):
        assert mode in ("declared", "content")
        self.mode = mode
        self.versions = {v["id"]: v for v in revision["state_versions"]}
        self.by_hash = {content_hash(v): v["id"] for v in revision["state_versions"]}
        self.by_ts = {}
        self.ts_collisions = set()
        for v in revision["state_versions"]:
            t = v["produced_at"]
            if t in self.by_ts:
                self.ts_collisions.add(t)
            self.by_ts[t] = v["id"]
        self.declared = dict(revision.get("aliases_declared", {}))

    def resolve(self, token):
        """Return (canonical_id | None, route taken)."""
        if token in self.versions:
            return token, "serial"

        if isinstance(token, str) and token.startswith("sha256:"):
            if self.mode == "content":
                if token in self.by_hash:
                    return self.by_hash[token], "content hash (recomputed)"
                return None, "hash cannot be recomputed from any version content -> unverifiable"
            # declared mode: consult the table first, fall back to recomputation
            if token in self.declared:
                return self.declared[token], "declared alias (credibility not guaranteed by this function)"
            if token in self.by_hash:
                return self.by_hash[token], "content hash (fallback)"
            return None, "hash is neither in the declared table nor recomputable"

        if token in self.by_ts:
            if token in self.ts_collisions:
                return self.by_ts[token], "timestamp (collision! several versions at one instant -> single-value assumption broken)"
            return self.by_ts[token], "timestamp"

        return None, "unresolvable"

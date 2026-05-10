"""Keyed DataFrames for the Data Agent (in-memory)."""

from __future__ import annotations


class TabularStore:
    __slots__ = ("frames",)

    def __init__(self) -> None:
        self.frames: dict[str, object] = {}

    def clear(self) -> None:
        self.frames.clear()

    def replace_all(self, new_frames: dict[str, object]) -> None:
        self.clear()
        self.frames.update(new_frames)

    def as_dict(self) -> dict[str, object]:
        return dict(self.frames)

    def nonempty(self) -> bool:
        return bool(self.frames)

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from generate_log import build_markdown


def test_build_markdown_normal():
    """通常データでMarkdownが正しく生成されるか"""
    md = build_markdown(
        date="2026-04-18",
        steps=12000,
        distance=8.5,
        coding_str="2h 30m",
        commit_count=3,
        commit_messages=["fix bug", "add feature", "update README"]
    )
    assert "# 2026-04-18" in md
    assert "歩数 12000歩 / 8.5km" in md
    assert "2h 30m" in md
    assert "3 commits" in md
    assert "fix bug" in md
    assert "add feature" in md
    assert "update README" in md
    print("✅ test_build_markdown_normal passed")


def test_build_markdown_zero_steps():
    """歩数が0の場合でもエラーにならないか"""
    md = build_markdown(
        date="2026-04-18",
        steps=0,
        distance=0.0,
        coding_str="0h 0m",
        commit_count=0,
        commit_messages=[]
    )
    assert "歩数 0歩 / 0.0km" in md
    assert "0h 0m" in md
    assert "0 commits" in md
    print("✅ test_build_markdown_zero_steps passed")


def test_build_markdown_missing_health():
    """HealthKitデータが取得できなかった場合（—）でもエラーにならないか"""
    md = build_markdown(
        date="2026-04-18",
        steps="—",
        distance="—",
        coding_str="1h 15m",
        commit_count=2,
        commit_messages=["commit A"]
    )
    assert "歩数 —歩 / —km" in md
    assert "commit A" in md
    print("✅ test_build_markdown_missing_health passed")


def test_build_markdown_no_commits():
    """コミットがない日のコミットメッセージ行が空になるか"""
    md = build_markdown(
        date="2026-04-18",
        steps=5000,
        distance=3.5,
        coding_str="0h 45m",
        commit_count=0,
        commit_messages=[]
    )
    assert "└" not in md
    print("✅ test_build_markdown_no_commits passed")


if __name__ == "__main__":
    test_build_markdown_normal()
    test_build_markdown_zero_steps()
    test_build_markdown_missing_health()
    test_build_markdown_no_commits()
    print("\n✅ All tests passed")

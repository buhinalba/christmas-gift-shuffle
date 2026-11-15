from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from christmas_gift_shuffle.application.interfaces.interfaces import GiftLine, RenderedEmail


class JinjaAssignmentEmailRenderer:
    def __init__(self, template_dir: Path | None = None):
        template_dir = template_dir or Path(__file__).parent / "templates"
        self._env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(["html"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def render(self, exchange_name: str, buyer_name: str,
               gifts: list[GiftLine]) -> RenderedEmail:
        ctx = {"exchange_name": exchange_name, "buyer_name": buyer_name, "gifts": gifts}
        return RenderedEmail(
            subject=f"{exchange_name}",
            exchange_name = exchange_name,
            text=self._env.get_template("assignment.txt").render(**ctx),
            html=self._env.get_template("assignment.html").render(**ctx),
        )
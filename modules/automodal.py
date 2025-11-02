from typing import Dict, Tuple

import discord

from modules.regex_patterns import URL_RE

typecheckers = {
    "int": lambda x: str(x).isnumeric(),
    "float": lambda x: str(x).isdecimal(),
    "number": lambda x: str(x).isnumeric() or str(x).isdecimal(),
    "url": lambda x: URL_RE.match(x),
    "string": lambda x: True,
}

typeconverters = {
    "int": lambda x: int(x),
    "float": lambda x: float(x),
    "number": lambda x: int(x) if str(x).isnumeric() else float(x),
    "url": lambda x: str(x),
    "string": lambda x: str(x),
}


example_fields = {
    "link": {
        "type": "url",
        "label": "Audio URL",
        "required": True,
        "default": "https://www.example.com",
        "placeholder": "the URL to download",
        "length": (10, 200)
    },
    "duration": {
        "type": "number",
        "required": True,
        "label": "Amount to cut",
        "default": 12,
        "placeholder": "the length to cut",
        "length": (5, 15)
    }
}

def automodal(title: str, fields, submit_handler):
    class AutoModal(discord.ui.Modal, title=title):
        def __init__(self):
            super().__init__()
            self.inputs = {}

            for name, config in fields.items():
                kwargs = {
                    "label": f"[{config['type']}] {config.get('label', name)}",
                    "placeholder": config.get("placeholder", ""),
                    "default": str(config.get("default", "")),
                    "required": config.get("required", False),
                }

                if config["type"] in ["string", "url"] and "length" in config:
                    kwargs["min_length"], kwargs["max_length"] = config["length"]

                input_field = discord.ui.TextInput(**kwargs)
                self.inputs[name] = input_field
                self.add_item(input_field)

        async def on_submit(self, interaction: discord.Interaction):
            values = {}
            for name, field in self.inputs.items():
                config = fields[name]
                raw_value = field.value.strip()
                field_type = config["type"]

                if not typecheckers[field_type](raw_value):
                    await interaction.response.send_message(
                        f"The field {name} should be a {field_type}! You entered: `{raw_value}`", ephemeral=True
                    )
                    return

                values[name] = typeconverters[field_type](raw_value)

            await submit_handler(interaction, **values)

    return AutoModal()
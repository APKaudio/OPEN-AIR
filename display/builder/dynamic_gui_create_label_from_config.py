# display/builder/dynamic_gui_create_label_from_config.py
#
# A mixin class for the DynamicGuiBuilder that handles creating a label from a config dictionary.
#
# Author: Anthony Peter Kuzub
# Blog: www.Like.audio (Contributor to this project)
#
# Professional services for customizing and tailoring this software to your specific
# application can be negotiated. There is no charge to use, modify, or fork this software.
#
# Build Log: https://like.audio/category/software/spectrum-scanner/
# Source Code: https://github.com/APKaudio/
# Feature Requests can be emailed to i @ like . audio
#
#
# Version 20251127.000000.1

import os

# --- Global Scope Variables ---
current_version = "20251127.000000.1"
current_version_hash = (20251127 * 0 * 1)
current_file = f"{os.path.basename(__file__)}"


class LabelFromConfigCreatorMixin:
    """
    A mixin class that provides a wrapper for creating a label widget
    from a configuration dictionary.
    """
    def _create_label_from_config(self, parent_frame, label, config, path):
        # A wrapper for _create_label to match the factory function signature.
        # It calls the _create_label method (provided by LabelCreatorMixin).
        return self._create_label(
            parent_frame=parent_frame,
            label=label,
            value=config.get("value"),
            units=config.get("units"),
            path=path
        )
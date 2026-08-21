import json
import os

MCTIERS_PRESETS = {
    "crystal": {
        "enabled": True,
        "name": "McTiers Crystal",
        "server_id": "898743810207653919",
        "channel_id": "898743810207653919",
        "bot_id": "1124128173609713734",
        "logo": "https://images-ext-1.discordapp.net/external/4Y4yKdubuCrgZCEF1om__A5XVeLrMfZF23-sj6KArW4/https/cdn.discordapp.com/icons/898743810207653919/f0567dc82a9fd0728bf75c23790a5327.png?format=webp&quality=lossless"
    },
    "sw": {
        "enabled": True,
        "name": "McTiers Sw (Sword)",
        "server_id": "1317975081976332338",
        "channel_id": "1317975085470187623",
        "bot_id": "1124128173609713734",
        "logo": "https://images-ext-1.discordapp.net/external/xXYKolnRFyE1tpoh8nG3_isKzefvgAYs2LuLHfipnZ8/%3Fsize%3D4096/https/cdn.discordapp.com/icons/1317975081976332338/fee96fb5d4c69bc55a400023dbf839b8.png?format=webp&quality=lossless"
    },
    "smp": {
        "enabled": True,
        "name": "McTiers Smp",
        "server_id": "1224245679749206050",
        "channel_id": "1224245683335462969",
        "bot_id": "1124128173609713734",
        "logo": "https://images-ext-1.discordapp.net/external/GjRgcD2jdEiHrO_QSbZ7XeWF5c299CKottpFgBIrkVs/%3Fsize%3D4096/https/cdn.discordapp.com/icons/1224245679749206050/137e5c98c628b454504ca99c0d6a9536.png?format=webp&quality=lossless&width=192&height=192"
    },
    "netherite_pot": {
        "enabled": True,
        "name": "McTiers Netherite Pot",
        "server_id": "1317971630886227998",
        "channel_id": "1317971632484126791",
        "bot_id": "1124128173609713734",
        "logo": "https://images-ext-1.discordapp.net/external/YIyMU7GUG8ZvRmczbKgHgw-yl1yDZmUtCKC3avY776M/%3Fsize%3D4096/https/cdn.discordapp.com/icons/1317971630886227998/3f472c84b0be45061b005e17c0a109f4.png?format=webp&quality=lossless"
    },
    "dia_pot": {
        "enabled": True,
        "name": "McTiers Dia Pot",
        "server_id": "1317974023384334426",
        "channel_id": "1317974027922309133",
        "bot_id": "1124128173609713734",
        "logo": "https://images-ext-1.discordapp.net/external/onAdwdICQ8zFfLVNI6Z3rHEMzCHwByToNLUAmyB6_co/%3Fsize%3D4096/https/cdn.discordapp.com/icons/1317974023384334426/2af41699c1ccaa3f072d533c6610bb4a.png?format=webp&quality=lossless"
    },
    "uhc": {
        "enabled": True,
        "name": "McTiers UHC",
        "server_id": "1316948661384646767",
        "channel_id": "1316948663095791623",
        "bot_id": "1124128173609713734",
        "logo": "https://images-ext-1.discordapp.net/external/xgdVDQGxwBupAb2MlnXKFmFDjX_YlxnYedx5jVqQ4yk/%3Fsize%3D4096/https/cdn.discordapp.com/icons/1316948661384646767/c4a4637ee780847a8bed935b23ceb290.png?format=webp&quality=lossless&width=192&height=192"
    },
    "mace": {
        "enabled": True,
        "name": "McTiers Mace",
        "server_id": "1187058381849112606",
        "channel_id": "1306853800547581963",
        "bot_id": "1124128173609713734",
        "logo": "https://images-ext-1.discordapp.net/external/baqkLlJkn0RJlIhNgRT3y-lNIjF6H5BqxmKK5Y78lkg/%3Fsize%3D4096/https/cdn.discordapp.com/icons/1187058381849112606/2aaa555030ca7f61560b89cc00880e20.png?format=webp&quality=lossless"
    },
    "axe_shield": {
        "enabled": True,
        "name": "McTiers Axe and Shield",
        "server_id": "1317974470132240424",
        "channel_id": "1317974473617707094",
        "bot_id": "1124128173609713734",
        "logo": "https://images-ext-1.discordapp.net/external/ix7udav1xOhuiEz3Gesk2baZE6gi8XaD-IkV1_EvFWc/%3Fsize%3D4096/https/cdn.discordapp.com/icons/1317974470132240424/9d4311fbe3d8cd980473555284bf595d.png?format=webp&quality=lossless"
    }
}

PVPTIERS_PRESETS = {
    "crystal": {
        "enabled": True,
        "name": "PvPtiers Crystal",
        "server_id": "898743810207653919",
        "channel_id": "1333182374271254568",
        "bot_id": "1328378417145446440",
        "logo": "https://images-ext-1.discordapp.net/external/knNxKpXjuLt9ojuCI57YzZxuP1kYqq7PlYeqFuJv7ic/%3Fsize%3D512/https/cdn.discordapp.com/icons/1333178700883034269/ef652f451a176ff1fe9d6d4449315dc1.png?format=webp&quality=lossless"
    },
    "sword": {
        "enabled": True,
        "name": "PvPtiers Sword",
        "server_id": "513709294844117013",
        "channel_id": "984399701904347197",
        "bot_id": "1328378417145446440",
        "logo": "https://images-ext-1.discordapp.net/external/UA_PSb2gcroZmeLAHsH7KB4eJM2u7YnyG45XG4GJa9w/%3Fsize%3D512/https/cdn.discordapp.com/icons/513709294844117013/d416c244360a171124c92354a142604d.png?format=webp&quality=lossless"
    },
    "smp": {
        "enabled": True,
        "name": "PvPtiers SMP",
        "server_id": "981948043903533176",
        "channel_id": "1059958212687839382",
        "bot_id": "1328378417145446440",
        "logo": "https://images-ext-1.discordapp.net/external/DKJUBn3vRQDahdZtBM7xITNCeMuhC-G1smDeerfBiB0/%3Fsize%3D512/https/cdn.discordapp.com/icons/981948043903533176/a5edb1bf548326547f356a051c3f965a.png?format=webp&quality=lossless"
    },
    "nethpot": {
        "enabled": True,
        "name": "PvPtiers NethPot",
        "server_id": "875309328607899658",
        "channel_id": "1005941425793400863",
        "bot_id": "1328378417145446440",
        "logo": "https://images-ext-1.discordapp.net/external/D1McPf4EItXyOsjouYLIix1-DFifAhwV6voIs8nu1AY/%3Fsize%3D512/https/cdn.discordapp.com/icons/875309328607899658/80182749367c293a6c6ff6318aadb9c4.png?format=webp&quality=lossless&width=320&height=320"
    },
    "diapot": {
        "enabled": True,
        "name": "PvPtiers DiaPot",
        "server_id": "1007038689412665404",
        "channel_id": "1125430210200862772",
        "bot_id": "1328378417145446440",
        "logo": "https://images-ext-1.discordapp.net/external/GjaafFAcS7yevb5sMGbMvAeODdMzoSgznlDJoz9JR9c/%3Fsize%3D512/https/cdn.discordapp.com/icons/1007038689412665404/c1f795f90a215dff4faec5d259ad9135.png?format=webp&quality=lossless"
    },
    "uhc": {
        "enabled": True,
        "name": "PvPtiers UHC",
        "server_id": "860880412975824898",
        "channel_id": "1012663179697991733",
        "bot_id": "1328378417145446440",
        "logo": "https://images-ext-1.discordapp.net/external/0AOVdtPR3IKR7WYsq8KpXmczV0B5HOstw9vygy8KE8M/%3Fsize%3D512/https/cdn.discordapp.com/icons/860880412975824898/4e3b3454978a0157484a261c23adc607.png?format=webp&quality=lossless"
    },
    "mace": {
        "enabled": True,
        "name": "PvPtiers Mace",
        "server_id": "1187058381849112606",
        "channel_id": "1395704405977862144",
        "bot_id": "1328378417145446440",
        "logo": "https://images-ext-1.discordapp.net/external/wCVxoqwEBXPfWj-_WQOgRRoD5zjcEgoG9t-qZsiIFXE/%3Fsize%3D512/https/cdn.discordapp.com/icons/1345939343448997908/68d2cca9dbacb84cb9cb6f0db72b2676.png?format=webp&quality=lossless&width=320&height=320"
    },
    "axe": {
        "enabled": True,
        "name": "PvPtiers Axe",
        "server_id": "896903597709754398",
        "channel_id": "1060546468580184114",
        "bot_id": "1328378417145446440",
        "logo": "https://images-ext-1.discordapp.net/external/x5GJ3J_irDD7lJm6z5Ob-khjeeYGNS8AWuT0Je_rfSY/%3Fsize%3D512/https/cdn.discordapp.com/icons/896903597709754398/eb1a1048d3f7fb738dd1849163025c0b.png?format=webp&quality=lossless"
    }
}

CUSTOM_PRESETS = {
    "custom_1": {
        "enabled": True,
        "name": "Custom Server 1",
        "server_id": "",
        "channel_id": "",
        "bot_id": ""
    }
}

DEFAULT_CONFIG = {
    "user_token": "",
    "webhook_url": "",
    "webhook_enabled": True,
    "global_settings": {
        "click_mode": "turbo",
        "sound_alert": True,
        "sound_volume": 80,
        "constellation": True,
        "anti_screenshot": True
    },
    "mctiers_channels": MCTIERS_PRESETS,
    "pvptiers_channels": PVPTIERS_PRESETS,
    "custom_channels": CUSTOM_PRESETS,
    "mctiers": {
        "name": "MCTIERS",
        "join_button_labels": ["Join Queue", "Join", "Queue"]
    },
    "pvptiers": {
        "name": "PVPTIERS",
        "join_button_labels": ["Join Queue", "Join", "Queue"]
    },
    "custom": {
        "name": "CUSTOM SERVERS",
        "join_button_labels": ["Join Queue", "Join", "Queue"]
    },
    "hwid_settings": {
        "enabled": True,
        "whitelist_url": "",
        "allowed_hwids": []
    }
}

class ConfigManager:
    def __init__(self, filename="config.json"):
        if not os.path.isabs(filename):
            import sys
            if getattr(sys, 'frozen', False):
                base_dir = os.path.dirname(sys.executable)
            else:
                base_dir = os.path.dirname(os.path.abspath(__file__))
            self.filename = os.path.join(base_dir, filename)
        else:
            self.filename = filename
        self.config = self.load_config()

    def load_config(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                    for key, val in DEFAULT_CONFIG.items():
                        if key not in cfg:
                            cfg[key] = val
                    return cfg
            except Exception as e:
                print(f"[CONFIG] Error loading {self.filename}: {e}")
        return DEFAULT_CONFIG.copy()

    def save_config(self, new_config):
        try:
            self.config.update(new_config)
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"[CONFIG] Error saving {self.filename}: {e}")
            return False

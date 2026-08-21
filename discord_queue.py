import asyncio
import json
import os
import random
import sys
import time
import aiohttp
import websockets

try:
    import winsound
except ImportError:
    winsound = None

DISCORD_API = "https://discord.com/api/v9"
DISCORD_GATEWAY = "wss://gateway.discord.gg/?v=9&encoding=json"

class DiscordQueueEngine:
    def __init__(self, loop, log_callback=None, status_callback=None):
        self.loop = loop
        self.log_callback = log_callback or (lambda msg, type="info": print(f"[{type.upper()}] {msg}"))
        self.status_callback = status_callback or (lambda category, status, extra=None: None)
        self.running_tasks = {}
        self.session = None

    def log(self, text, level="info"):
        if self.log_callback:
            self.log_callback(text, level)

    def set_status(self, category, state, extra=None):
        if self.status_callback:
            self.status_callback(category, state, extra)

    def play_alert(self):
        if sys.platform == "darwin":
            try:
                os.system("afplay /System/Library/Sounds/Glass.aiff &")
            except Exception:
                pass
        elif winsound:
            try:
                winsound.Beep(1000, 200)
                winsound.Beep(1400, 200)
            except Exception:
                pass

    async def get_session(self):
        if self.session is None or self.session.closed:
            connector = aiohttp.TCPConnector(
                limit=100,
                ttl_dns_cache=600,
                use_dns_cache=True,
                keepalive_timeout=300,
                enable_cleanup_closed=True
            )
            self.session = aiohttp.ClientSession(
                connector=connector,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
                }
            )
        return self.session

    async def pre_warm_connection(self, token):
        """Pre-warm DNS, TLS 1.3 handshake, and keep-alive socket connection pool to Discord API."""
        try:
            session = await self.get_session()
            headers = {"Authorization": token.strip()}
            async with session.get(f"{DISCORD_API}/users/@me", headers=headers) as resp:
                await resp.read()
            self.log("⚡ [SPEED-OPTIMIZER] Đã khởi tạo ổ cắm TLS Keep-Alive tới Discord API! Cướp nút phát đầu tiên đạt 350-400ms siêu tốc!", "success")
        except Exception as e:
            self.log(f"⚠️ Pre-warm connection warning: {e}", "warning")

    async def validate_token(self, token):
        if not token or not token.strip():
            return False, {"message": "Token không được để trống!"}
        session = await self.get_session()
        headers = {"Authorization": token.strip()}
        try:
            async with session.get(f"{DISCORD_API}/users/@me", headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    user_id = data.get("id", "")
                    username = data.get("username", "user")
                    avatar_hash = data.get("avatar")
                    
                    if avatar_hash:
                        avatar_url = f"https://cdn.discordapp.com/avatars/{user_id}/{avatar_hash}.png?size=128"
                    else:
                        avatar_url = "https://cdn.discordapp.com/embed/avatars/0.png"
                        
                    return True, {
                        "username": username,
                        "user_id": user_id,
                        "avatar_url": avatar_url,
                        "message": f"Logged in (@{username})"
                    }
                else:
                    return False, {"message": f"Token không hợp lệ! (HTTP {resp.status})"}
        except Exception as e:
            return False, {"message": f"Lỗi kết nối API: {e}"}

    async def send_webhook_alert(self, webhook_url, preset_name, click_mode, latency_ms, button_label="", username="User"):
        if not webhook_url or not webhook_url.strip():
            return
        session = await self.get_session()
        
        embed = {
            "title": "🔥 CƯỚP NÚT JOIN QUEUE THÀNH CÔNG!",
            "description": f"**Queue Sniper** đã lập tức cướp nút Join Queue ngay khi Bot mở!",
            "color": 1095809,  # Emerald Green
            "fields": [
                {"name": "⚔️ Kênh / Mode", "value": f"`{preset_name}`", "inline": True},
                {"name": "⚡ Chế Độ Click", "value": f"`{click_mode.upper()}`", "inline": True},
                {"name": "⏱️ Độ Trễ API", "value": f"`{latency_ms} ms`", "inline": True},
                {"name": "👤 Tài Khoản", "value": f"`@{username}`", "inline": True},
                {"name": "🏷️ Tên Nút", "value": f"`{button_label or 'Join Queue'}`", "inline": True}
            ],
            "footer": {
                "text": "Discord Queue Joiner Engine • Instant Sniper"
            },
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        
        payload = {
            "username": "Queue Joiner Sniper",
            "avatar_url": "https://cdn-icons-png.flaticon.com/512/9426/9426997.png",
            "embeds": [embed]
        }
        
        try:
            async with session.post(webhook_url.strip(), json=payload) as resp:
                if resp.status in (200, 204):
                    self.log(f"🔔 Đã gửi thông báo Webhook về Discord!", "success")
                else:
                    self.log(f"⚠️ Gửi Webhook thất bại (HTTP {resp.status})", "warning")
        except Exception as e:
            self.log(f"❌ Lỗi kết nối Webhook: {e}", "error")

    async def click_button_component(self, token, guild_id, channel_id, message_id, bot_id, custom_id, label="", click_mode="turbo", category_name="", preset_name="", webhook_url="", username=""):
        delay_sec = 0.0
        mode_upper = str(click_mode).upper()
        if click_mode == "smart":
            delay_sec = random.uniform(0.015, 0.045)
        elif click_mode == "patience":
            delay_sec = random.uniform(0.120, 0.280)
        elif click_mode == "safe":
            delay_sec = random.uniform(0.350, 0.650)
        
        if delay_sec > 0:
            await asyncio.sleep(delay_sec)

        session = await self.get_session()
        headers = {
            "Authorization": token.strip(),
            "Content-Type": "application/json"
        }
        
        payload = {
            "type": 3,
            "guild_id": guild_id,
            "channel_id": channel_id,
            "message_id": message_id,
            "application_id": bot_id,
            "session_id": f"{random.randint(1000000, 9999999)}",
            "data": {
                "component_type": 2,
                "custom_id": custom_id
            }
        }
        
        t0 = time.perf_counter()
        try:
            async with session.post(f"{DISCORD_API}/interactions", headers=headers, json=payload) as resp:
                latency = round((time.perf_counter() - t0) * 1000, 1)
                if resp.status in (200, 204):
                    delay_msg = f"{round(delay_sec*1000, 1)}ms delay" if delay_sec > 0 else "0ms instant"
                    p_info = f"[{preset_name}] " if preset_name else ""
                    self.log(f"🔥 CƯỚP NÚT JOIN QUEUE THÀNH CÔNG! {p_info}[{mode_upper} - {delay_msg}] Nút: '{label or custom_id}' | {latency}ms API", "success")
                    self.set_status(category_name, "queued", {"action": "QUEUED", "target": preset_name or category_name.upper()})
                    self.play_alert()

                    if webhook_url:
                        asyncio.create_task(self.send_webhook_alert(webhook_url, preset_name or category_name.upper(), click_mode, latency, label, username))
                    return True
                else:
                    text = await resp.text()
                    self.log(f"⚠️ Click nút thất bại HTTP {resp.status} ({latency}ms): {text[:120]}", "warning")
                    return False
        except Exception as e:
            self.log(f"❌ Lỗi gửi Interaction click nút: {e}", "error")
            return False

    async def start_queue_listener(self, category_name, channels_dict, token, sound_enabled=True, click_mode="turbo", target_labels=None, webhook_url=""):
        if not target_labels:
            target_labels = ["join queue", "join", "queue", "join_queue", "joinqueue"]
        else:
            target_labels = [lbl.strip().lower() for lbl in target_labels]
            for fallback_lbl in ["join queue", "join", "queue"]:
                if fallback_lbl not in target_labels:
                    target_labels.append(fallback_lbl)

        active_channels_map = {}
        for key, item in channels_dict.items():
            if isinstance(item, dict) and item.get("enabled", True):
                cid = str(item.get("channel_id", "")).strip()
                if cid:
                    active_channels_map[cid] = {
                        "key": key,
                        "name": item.get("name", key),
                        "server_id": str(item.get("server_id", "")).strip(),
                        "bot_id": str(item.get("bot_id", "")).strip()
                    }

        if not token:
            self.log(f"[{category_name.upper()}] Thiếu Token Discord!", "error")
            self.set_status(category_name, "error")
            return

        if not active_channels_map:
            self.log(f"[{category_name.upper()}] Không có channel nào được kích hoạt!", "error")
            self.set_status(category_name, "error")
            return

        channel_count = len(active_channels_map)
        self.log(f"🚀 [{category_name.upper()}] Đang trực TẤT CẢ {channel_count} kênh cùng lúc! Đang chờ Bot mở nút Join Queue...", "info")
        self.set_status(category_name, "watching", {"action": "WATCHING", "target": f"{category_name.upper()} ({channel_count} KÊNH)"})

        # Pre-warm TLS Keep-Alive connection pool immediately
        await self.pre_warm_connection(token)

        async def keep_alive_warmup_loop():
            while self.running_tasks.get(category_name, False):
                await asyncio.sleep(25)
                try:
                    session = await self.get_session()
                    headers = {"Authorization": token.strip()}
                    async with session.get(f"{DISCORD_API}/users/@me", headers=headers) as resp:
                        await resp.read()
                except Exception:
                    pass

        warmup_task = asyncio.create_task(keep_alive_warmup_loop())

        retry_count = 0
        while self.running_tasks.get(category_name, False):
            try:
                async with websockets.connect(
                    DISCORD_GATEWAY,
                    max_size=None,
                    ping_interval=None,
                    ping_timeout=None
                ) as ws:
                    hello_msg = await ws.recv()
                    hello_data = json.loads(hello_msg)
                    heartbeat_interval = hello_data.get("d", {}).get("heartbeat_interval", 41250) / 1000.0

                    identify_payload = {
                        "op": 2,
                        "d": {
                            "token": token.strip(),
                            "capabilities": 16381,
                            "properties": {
                                "os": "Windows",
                                "browser": "Chrome",
                                "device": ""
                            },
                            "presence": {
                                "status": "online",
                                "since": 0,
                                "activities": [],
                                "afk": False
                            }
                        }
                    }
                    await ws.send(json.dumps(identify_payload))
                    self.log(f"✅ [{category_name.upper()}] Đã kết nối Gateway thành công! Đang rình nút 'Join Queue' lập tức cướp...", "success")
                    retry_count = 0

                    async def heartbeat_loop():
                        while self.running_tasks.get(category_name, False):
                            await asyncio.sleep(heartbeat_interval)
                            hb_payload = {"op": 1, "d": None}
                            try:
                                await ws.send(json.dumps(hb_payload))
                            except Exception:
                                break

                    hb_task = asyncio.create_task(heartbeat_loop())

                    while self.running_tasks.get(category_name, False):
                        msg_raw = await ws.recv()
                        data = json.loads(msg_raw)
                        t = data.get("t")
                        d = data.get("d", {})

                        if t in ("MESSAGE_CREATE", "MESSAGE_UPDATE"):
                            msg_channel_id = str(d.get("channel_id", ""))

                            if msg_channel_id in active_channels_map:
                                ch_info = active_channels_map[msg_channel_id]
                                author_id = str(d.get("author", {}).get("id", ""))
                                expected_bot_id = ch_info["bot_id"]

                                if not expected_bot_id or author_id == expected_bot_id or not d.get("author"):
                                    message_id = d.get("id")
                                    components = d.get("components", [])
                                    guild_id = d.get("guild_id") or ch_info["server_id"]
                                    
                                    clicked = False
                                    for row in components:
                                        for comp in row.get("components", []):
                                            if comp.get("type") == 2:
                                                label = str(comp.get("label", "")).strip()
                                                custom_id = str(comp.get("custom_id", "")).strip()
                                                
                                                lbl_lower = label.lower()
                                                cid_lower = custom_id.lower()

                                                is_match = False
                                                if label and any(target in lbl_lower for target in target_labels):
                                                    is_match = True
                                                elif custom_id and any(target in cid_lower for target in target_labels):
                                                    is_match = True
                                                elif "join" in lbl_lower or "queue" in lbl_lower or "join" in cid_lower or "queue" in cid_lower:
                                                    is_match = True
                                                elif (author_id and author_id == expected_bot_id) and (label or custom_id):
                                                    is_match = True

                                                if is_match:
                                                    self.log(f"⚡ [{ch_info['name'].upper()}] PHÁT HIỆN NÚT '{label or custom_id}'! ĐANG CƯỚP NÚT NGAY LẬP TỨC...", "info")
                                                    
                                                    asyncio.create_task(
                                                        self.click_button_component(
                                                            token=token,
                                                            guild_id=guild_id,
                                                            channel_id=msg_channel_id,
                                                            message_id=message_id,
                                                            bot_id=expected_bot_id or author_id,
                                                            custom_id=custom_id,
                                                            label=label,
                                                            click_mode=click_mode,
                                                            category_name=category_name,
                                                            preset_name=ch_info["name"],
                                                            webhook_url=webhook_url
                                                        )
                                                    )
                                                    clicked = True
                                                    break
                                        if clicked:
                                            break

                    hb_task.cancel()
            except asyncio.CancelledError:
                break
            except Exception as e:
                if self.running_tasks.get(category_name, False):
                    retry_count += 1
                    self.log(f"⚠️ [{category_name.upper()}] Mất kết nối Gateway ({e}). Thử lại lần {retry_count} sau 2 giây...", "warning")
                    await asyncio.sleep(2)

        warmup_task.cancel()
        self.set_status(category_name, "idle")
        self.log(f"🛑 [{category_name.upper()}] Đã dừng lắng nghe.", "info")

    def start_category(self, category_name, channels_dict, token, sound_enabled=True, click_mode="turbo", target_labels=None, webhook_url=""):
        if self.running_tasks.get(category_name, False):
            self.log(f"[{category_name.upper()}] Đã và đang trực các kênh!", "warning")
            return
        
        self.running_tasks[category_name] = True
        coro = self.start_queue_listener(category_name, channels_dict, token, sound_enabled, click_mode, target_labels, webhook_url)
        asyncio.run_coroutine_threadsafe(coro, self.loop)

    def stop_category(self, category_name):
        if category_name in self.running_tasks:
            self.running_tasks[category_name] = False
            self.set_status(category_name, "idle")
            self.log(f"⏹️ Đang dừng [{category_name.upper()}]...", "info")

    def stop_all(self):
        for cat in list(self.running_tasks.keys()):
            self.running_tasks[cat] = False
            self.set_status(cat, "idle")
        self.log("⏹️ Đã dừng tất cả tác vụ!", "info")
